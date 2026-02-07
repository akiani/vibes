use axum::extract::{Path, State};
use axum::response::sse::{Event, KeepAlive, Sse};
use axum::response::IntoResponse;
use axum::Json;
use chrono::Utc;
use futures::StreamExt;
use std::convert::Infallible;
use std::sync::Arc;
use uuid::Uuid;

use crate::errors::AppError;
use crate::llm::LlmProvider;
use crate::models::*;
use crate::store::Store;

pub type AppState = Arc<AppStateInner>;

pub struct AppStateInner {
    pub store: Store,
    pub llm: Box<dyn LlmProvider>,
}

// -- Session endpoints -------------------------------------------------------

pub async fn create_session(
    State(state): State<AppState>,
    Json(req): Json<CreateSessionRequest>,
) -> Result<impl IntoResponse, AppError> {
    let title = req.title.unwrap_or_else(|| "New Chat".into());
    let session = Session::new(title);
    let session = state.store.create_session(session).await;
    Ok((axum::http::StatusCode::CREATED, Json(session)))
}

pub async fn list_sessions(
    State(state): State<AppState>,
) -> Result<Json<Vec<SessionSummary>>, AppError> {
    let sessions = state.store.list_sessions().await;
    let summaries: Vec<SessionSummary> = sessions.iter().map(SessionSummary::from).collect();
    Ok(Json(summaries))
}

pub async fn get_session(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<Session>, AppError> {
    state
        .store
        .get_session(id)
        .await
        .map(Json)
        .ok_or_else(|| AppError::NotFound(format!("session {id} not found")))
}

pub async fn delete_session(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<impl IntoResponse, AppError> {
    if state.store.delete_session(id).await {
        Ok(axum::http::StatusCode::NO_CONTENT)
    } else {
        Err(AppError::NotFound(format!("session {id} not found")))
    }
}

// -- Chat endpoint -----------------------------------------------------------

pub async fn chat(
    State(state): State<AppState>,
    Path(session_id): Path<Uuid>,
    Json(req): Json<ChatRequest>,
) -> Result<impl IntoResponse, AppError> {
    let mut session = state
        .store
        .get_session(session_id)
        .await
        .ok_or_else(|| AppError::NotFound(format!("session {session_id} not found")))?;

    // Append the user message.
    let user_msg = Message::new(Role::User, req.message);
    session.messages.push(user_msg.clone());

    if req.stream {
        // -- Streaming path --------------------------------------------------
        let token_stream = state
            .llm
            .stream(&session.messages)
            .map_err(|e| AppError::Internal(e.to_string()))?;

        let msg_id = Uuid::new_v4();
        let store = state.store.clone();
        let accumulated = Arc::new(tokio::sync::Mutex::new(String::new()));

        // Map raw token chunks into SSE delta events, accumulating content.
        let acc = accumulated.clone();
        let delta_stream = token_stream.then(move |chunk| {
            let acc = acc.clone();
            async move {
                match chunk {
                    Ok(text) => {
                        acc.lock().await.push_str(&text);
                        let evt = StreamEvent::Delta { content: text };
                        Ok::<_, Infallible>(
                            Event::default().data(serde_json::to_string(&evt).unwrap()),
                        )
                    }
                    Err(e) => {
                        let evt = StreamEvent::Error { error: e.to_string() };
                        Ok(Event::default().data(serde_json::to_string(&evt).unwrap()))
                    }
                }
            }
        });

        // Start event.
        let start_evt = StreamEvent::Start { message_id: msg_id };
        let start_stream = futures::stream::once(async move {
            Ok::<_, Infallible>(
                Event::default().data(serde_json::to_string(&start_evt).unwrap()),
            )
        });

        // Done event — also persists the full assistant message.
        let session_messages = session.messages.clone();
        let done_stream = futures::stream::once({
            let accumulated = accumulated.clone();
            async move {
                let full_content = accumulated.lock().await.clone();
                let mut sess = store.get_session(session_id).await.unwrap();
                if sess.messages.len() < session_messages.len() {
                    sess.messages = session_messages;
                }
                let assistant_msg = Message {
                    id: msg_id,
                    role: Role::Assistant,
                    content: full_content,
                    created_at: Utc::now(),
                };
                sess.messages.push(assistant_msg);
                sess.updated_at = Utc::now();
                store.update_session(sess).await;
                let evt = StreamEvent::Done { message_id: msg_id };
                Ok::<_, Infallible>(
                    Event::default().data(serde_json::to_string(&evt).unwrap()),
                )
            }
        });

        let sse_stream = start_stream.chain(delta_stream).chain(done_stream);

        // Persist user message right away.
        session.updated_at = Utc::now();
        state.store.update_session(session).await;

        Ok(Sse::new(sse_stream).keep_alive(KeepAlive::default()).into_response())
    } else {
        // -- Non-streaming path ----------------------------------------------
        let response_text = state
            .llm
            .complete(&session.messages)
            .await
            .map_err(|e| AppError::Internal(e.to_string()))?;

        let assistant_msg = Message::new(Role::Assistant, response_text);
        session.messages.push(assistant_msg.clone());
        session.updated_at = Utc::now();
        state.store.update_session(session).await;

        Ok(Json(ChatResponse {
            message: assistant_msg,
        })
        .into_response())
    }
}
