use axum::body::Body;
use axum::http::{Request, StatusCode};
use http_body_util::BodyExt;
use std::sync::Arc;
use tower::util::ServiceExt;

use crate::llm::MockLlmProvider;
use crate::models::*;
use crate::routes::{AppState, AppStateInner};
use crate::store::Store;
use crate::build_router;

fn test_state() -> AppState {
    Arc::new(AppStateInner {
        store: Store::new(),
        llm: Box::new(MockLlmProvider),
    })
}

fn json_request(method: &str, uri: &str, body: Option<serde_json::Value>) -> Request<Body> {
    let builder = Request::builder()
        .method(method)
        .uri(uri)
        .header("content-type", "application/json");
    match body {
        Some(b) => builder
            .body(Body::from(serde_json::to_vec(&b).unwrap()))
            .unwrap(),
        None => builder.body(Body::empty()).unwrap(),
    }
}

async fn body_json<T: serde::de::DeserializeOwned>(body: Body) -> T {
    let bytes = body.collect().await.unwrap().to_bytes();
    serde_json::from_slice(&bytes).unwrap()
}

// -- Session CRUD tests ------------------------------------------------------

#[tokio::test]
async fn test_create_session() {
    let app = build_router(test_state());
    let req = json_request(
        "POST",
        "/sessions",
        Some(serde_json::json!({"title": "Test"})),
    );
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::CREATED);
    let session: Session = body_json(resp.into_body()).await;
    assert_eq!(session.title, "Test");
    assert!(session.messages.is_empty());
}

#[tokio::test]
async fn test_create_session_default_title() {
    let app = build_router(test_state());
    let req = json_request("POST", "/sessions", Some(serde_json::json!({})));
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::CREATED);
    let session: Session = body_json(resp.into_body()).await;
    assert_eq!(session.title, "New Chat");
}

#[tokio::test]
async fn test_list_sessions_empty() {
    let app = build_router(test_state());
    let req = json_request("GET", "/sessions", None);
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::OK);
    let list: Vec<SessionSummary> = body_json(resp.into_body()).await;
    assert!(list.is_empty());
}

#[tokio::test]
async fn test_list_sessions_after_create() {
    let state = test_state();

    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "A"})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::CREATED);

    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "B"})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::CREATED);

    let resp = build_router(state)
        .oneshot(json_request("GET", "/sessions", None))
        .await
        .unwrap();
    let list: Vec<SessionSummary> = body_json(resp.into_body()).await;
    assert_eq!(list.len(), 2);
}

#[tokio::test]
async fn test_get_session() {
    let state = test_state();

    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "Hello"})),
        ))
        .await
        .unwrap();
    let created: Session = body_json(resp.into_body()).await;

    let resp = build_router(state)
        .oneshot(json_request(
            "GET",
            &format!("/sessions/{}", created.id),
            None,
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::OK);
    let fetched: Session = body_json(resp.into_body()).await;
    assert_eq!(fetched.id, created.id);
    assert_eq!(fetched.title, "Hello");
}

#[tokio::test]
async fn test_get_session_not_found() {
    let app = build_router(test_state());
    let req = json_request(
        "GET",
        "/sessions/00000000-0000-0000-0000-000000000000",
        None,
    );
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn test_delete_session() {
    let state = test_state();

    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "Del"})),
        ))
        .await
        .unwrap();
    let created: Session = body_json(resp.into_body()).await;

    let resp = build_router(state.clone())
        .oneshot(json_request(
            "DELETE",
            &format!("/sessions/{}", created.id),
            None,
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::NO_CONTENT);

    // Verify it's gone.
    let resp = build_router(state)
        .oneshot(json_request(
            "GET",
            &format!("/sessions/{}", created.id),
            None,
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn test_delete_session_not_found() {
    let app = build_router(test_state());
    let req = json_request(
        "DELETE",
        "/sessions/00000000-0000-0000-0000-000000000000",
        None,
    );
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::NOT_FOUND);
}

// -- Chat tests --------------------------------------------------------------

#[tokio::test]
async fn test_chat_non_streaming() {
    let state = test_state();

    // Create a session.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "Chat"})),
        ))
        .await
        .unwrap();
    let session: Session = body_json(resp.into_body()).await;

    // Send a chat message (non-streaming).
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            &format!("/sessions/{}/chat", session.id),
            Some(serde_json::json!({"message": "Hello, world!", "stream": false})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::OK);

    let chat_resp: ChatResponse = body_json(resp.into_body()).await;
    assert_eq!(chat_resp.message.role, Role::Assistant);
    assert!(chat_resp.message.content.contains("mock response"));

    // Verify session now has 2 messages (user + assistant).
    let resp = build_router(state)
        .oneshot(json_request(
            "GET",
            &format!("/sessions/{}", session.id),
            None,
        ))
        .await
        .unwrap();
    let updated: Session = body_json(resp.into_body()).await;
    assert_eq!(updated.messages.len(), 2);
    assert_eq!(updated.messages[0].role, Role::User);
    assert_eq!(updated.messages[1].role, Role::Assistant);
}

#[tokio::test]
async fn test_chat_session_not_found() {
    let app = build_router(test_state());
    let req = json_request(
        "POST",
        "/sessions/00000000-0000-0000-0000-000000000000/chat",
        Some(serde_json::json!({"message": "hi"})),
    );
    let resp = app.oneshot(req).await.unwrap();
    assert_eq!(resp.status(), StatusCode::NOT_FOUND);
}

#[tokio::test]
async fn test_chat_streaming() {
    let state = test_state();

    // Create a session.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "Stream"})),
        ))
        .await
        .unwrap();
    let session: Session = body_json(resp.into_body()).await;

    // Send a streaming chat request.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            &format!("/sessions/{}/chat", session.id),
            Some(serde_json::json!({"message": "Tell me something", "stream": true})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::OK);

    // Collect the SSE body.
    let bytes = resp.into_body().collect().await.unwrap().to_bytes();
    let body_str = String::from_utf8(bytes.to_vec()).unwrap();

    // Should contain start, delta(s), and done events.
    assert!(
        body_str.contains("\"type\":\"start\""),
        "missing start event"
    );
    assert!(
        body_str.contains("\"type\":\"delta\""),
        "missing delta events"
    );
    assert!(body_str.contains("\"type\":\"done\""), "missing done event");

    // Wait briefly for the done handler to persist.
    tokio::time::sleep(std::time::Duration::from_millis(100)).await;

    // Verify session has messages persisted.
    let resp = build_router(state)
        .oneshot(json_request(
            "GET",
            &format!("/sessions/{}", session.id),
            None,
        ))
        .await
        .unwrap();
    let updated: Session = body_json(resp.into_body()).await;
    assert_eq!(updated.messages.len(), 2);
    assert_eq!(updated.messages[0].role, Role::User);
    assert_eq!(updated.messages[1].role, Role::Assistant);
    assert!(!updated.messages[1].content.is_empty());
}

#[tokio::test]
async fn test_chat_multi_turn() {
    let state = test_state();

    // Create a session.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            "/sessions",
            Some(serde_json::json!({"title": "Multi"})),
        ))
        .await
        .unwrap();
    let session: Session = body_json(resp.into_body()).await;

    // Turn 1.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            &format!("/sessions/{}/chat", session.id),
            Some(serde_json::json!({"message": "First message"})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::OK);

    // Turn 2.
    let resp = build_router(state.clone())
        .oneshot(json_request(
            "POST",
            &format!("/sessions/{}/chat", session.id),
            Some(serde_json::json!({"message": "Second message"})),
        ))
        .await
        .unwrap();
    assert_eq!(resp.status(), StatusCode::OK);

    // Verify 4 messages total (2 user + 2 assistant).
    let resp = build_router(state)
        .oneshot(json_request(
            "GET",
            &format!("/sessions/{}", session.id),
            None,
        ))
        .await
        .unwrap();
    let updated: Session = body_json(resp.into_body()).await;
    assert_eq!(updated.messages.len(), 4);
}

// -- Store unit tests --------------------------------------------------------

#[tokio::test]
async fn test_store_crud() {
    let store = Store::new();

    let session = crate::models::Session::new("Store test".into());
    let id = session.id;
    store.create_session(session).await;

    let fetched = store.get_session(id).await.unwrap();
    assert_eq!(fetched.title, "Store test");

    let list = store.list_sessions().await;
    assert_eq!(list.len(), 1);

    assert!(store.delete_session(id).await);
    assert!(store.get_session(id).await.is_none());
    assert!(!store.delete_session(id).await);
}

// -- LLM mock tests ----------------------------------------------------------

#[tokio::test]
async fn test_mock_llm_complete() {
    use crate::llm::LlmProvider;

    let provider = MockLlmProvider;
    let messages = vec![Message::new(Role::User, "Hello".into())];
    let result = provider.complete(&messages).await.unwrap();
    assert!(result.contains("mock response"));
    assert!(result.contains("Hello"));
}

#[tokio::test]
async fn test_mock_llm_stream() {
    use crate::llm::LlmProvider;
    use futures::StreamExt;

    let provider = MockLlmProvider;
    let messages = vec![Message::new(Role::User, "Hi there".into())];
    let mut stream = provider.stream(&messages).unwrap();

    let mut collected = String::new();
    while let Some(Ok(chunk)) = stream.next().await {
        collected.push_str(&chunk);
    }
    assert!(collected.contains("mock response"));
    assert!(collected.contains("Hi there"));
}
