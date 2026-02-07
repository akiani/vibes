use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;

use crate::models::Session;

/// Thread-safe in-memory session store.
#[derive(Clone)]
pub struct Store {
    sessions: Arc<RwLock<HashMap<Uuid, Session>>>,
}

impl Store {
    pub fn new() -> Self {
        Self {
            sessions: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn create_session(&self, session: Session) -> Session {
        let mut map = self.sessions.write().await;
        map.insert(session.id, session.clone());
        session
    }

    pub async fn get_session(&self, id: Uuid) -> Option<Session> {
        let map = self.sessions.read().await;
        map.get(&id).cloned()
    }

    pub async fn list_sessions(&self) -> Vec<Session> {
        let map = self.sessions.read().await;
        let mut sessions: Vec<Session> = map.values().cloned().collect();
        sessions.sort_by(|a, b| b.updated_at.cmp(&a.updated_at));
        sessions
    }

    pub async fn update_session(&self, session: Session) -> Option<Session> {
        let mut map = self.sessions.write().await;
        if map.contains_key(&session.id) {
            map.insert(session.id, session.clone());
            Some(session)
        } else {
            None
        }
    }

    pub async fn delete_session(&self, id: Uuid) -> bool {
        let mut map = self.sessions.write().await;
        map.remove(&id).is_some()
    }
}

impl Default for Store {
    fn default() -> Self {
        Self::new()
    }
}
