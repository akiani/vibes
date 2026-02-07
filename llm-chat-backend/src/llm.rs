use async_trait::async_trait;
use futures::Stream;
use std::pin::Pin;

use crate::models::Message;

/// A stream of string chunks produced by an LLM.
pub type TokenStream = Pin<Box<dyn Stream<Item = Result<String, LlmError>> + Send>>;

#[derive(Debug, thiserror::Error)]
pub enum LlmError {
    #[error("provider error: {0}")]
    Provider(String),
}

/// Trait that any LLM provider (Claude, mock, etc.) must implement.
#[async_trait]
pub trait LlmProvider: Send + Sync {
    /// Generate a complete (non-streaming) response.
    async fn complete(&self, messages: &[Message]) -> Result<String, LlmError>;

    /// Generate a streaming response, returning chunks of text.
    fn stream(&self, messages: &[Message]) -> Result<TokenStream, LlmError>;
}

// ---------------------------------------------------------------------------
// Mock provider — returns a canned response, token-by-token for streaming.
// ---------------------------------------------------------------------------

pub struct MockLlmProvider;

impl MockLlmProvider {
    fn generate_response(messages: &[Message]) -> String {
        let last = messages.last().map(|m| m.content.as_str()).unwrap_or("");
        format!(
            "This is a mock response to: \"{}\". In production this will come from Claude.",
            truncate(last, 80)
        )
    }
}

fn truncate(s: &str, max: usize) -> &str {
    if s.len() <= max {
        s
    } else {
        &s[..s.floor_char_boundary(max)]
    }
}

#[async_trait]
impl LlmProvider for MockLlmProvider {
    async fn complete(&self, messages: &[Message]) -> Result<String, LlmError> {
        let response = Self::generate_response(messages);
        // Simulate a tiny bit of latency.
        tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        Ok(response)
    }

    fn stream(&self, messages: &[Message]) -> Result<TokenStream, LlmError> {
        let response = Self::generate_response(messages);
        let words: Vec<String> = response
            .split_inclusive(' ')
            .map(|s| s.to_string())
            .collect();

        let stream = futures::stream::unfold(words.into_iter(), |mut iter| async move {
            let word = iter.next()?;
            tokio::time::sleep(std::time::Duration::from_millis(30)).await;
            Some((Ok(word), iter))
        });

        Ok(Box::pin(stream))
    }
}
