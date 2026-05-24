mod errors;
mod llm;
mod models;
mod routes;
mod store;

use axum::Router;
use axum::routing::{delete, get, post};
use std::sync::Arc;
use tower_http::cors::CorsLayer;
use tower_http::services::ServeDir;

use llm::MockLlmProvider;
use routes::{AppState, AppStateInner};
use store::Store;

pub fn build_router(state: AppState) -> Router {
    Router::new()
        .route("/sessions", post(routes::create_session))
        .route("/sessions", get(routes::list_sessions))
        .route("/sessions/{id}", get(routes::get_session))
        .route("/sessions/{id}", delete(routes::delete_session))
        .route("/sessions/{id}/chat", post(routes::chat))
        .layer(CorsLayer::permissive())
        .with_state(state)
}

#[tokio::main]
async fn main() {
    let state: AppState = Arc::new(AppStateInner {
        store: Store::new(),
        llm: Box::new(MockLlmProvider),
    });

    let api = build_router(state);
    let app = Router::new()
        .merge(api)
        .fallback_service(ServeDir::new("frontend"));

    let addr = "0.0.0.0:3001";
    println!("listening on {addr}");

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

#[cfg(test)]
mod tests;
