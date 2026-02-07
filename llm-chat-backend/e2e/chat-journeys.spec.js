const { test, expect } = require('@playwright/test');

const API = 'http://localhost:3001';

// Clean slate before each test: delete all existing sessions.
test.beforeEach(async ({ request }) => {
  const sessions = await (await request.get(`${API}/sessions`)).json();
  for (const s of sessions) {
    await request.delete(`${API}/sessions/${s.id}`);
  }
});

test.describe('Chat User Journeys', () => {

  test('01 - Landing page shows empty state', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.empty-title')).toHaveText('Start a conversation');
    await expect(page.locator('.empty-subtitle')).toHaveText('Create a new chat to begin');
    await page.screenshot({ path: 'screenshots/01-landing-empty-state.png' });
  });

  test('02 - Create a new chat session', async ({ page }) => {
    await page.goto('/');
    await page.click('#new-chat');
    await expect(page.locator('#chat-form')).toBeVisible();
    await expect(page.locator('.session-item')).toHaveCount(1);
    await page.screenshot({ path: 'screenshots/02-new-session-created.png' });
  });

  test('03 - Send a message and receive a streamed response', async ({ page }) => {
    await page.goto('/');
    await page.click('#new-chat');
    await expect(page.locator('#chat-form')).toBeVisible();

    await page.fill('#message-input', 'Hello, how are you?');
    await page.screenshot({ path: 'screenshots/03a-message-typed.png' });

    await page.click('#send-btn');

    // Wait for the assistant response to finish streaming.
    await expect(page.locator('.message.assistant .bubble')).toBeVisible({ timeout: 15000 });
    await page.waitForFunction(() => {
      const bubble = document.querySelector('.message.assistant .bubble');
      return bubble && !bubble.classList.contains('streaming');
    }, { timeout: 15000 });

    await page.screenshot({ path: 'screenshots/03b-first-response-received.png' });

    const messages = page.locator('.message');
    await expect(messages).toHaveCount(2);
    await expect(messages.nth(0)).toHaveClass(/user/);
    await expect(messages.nth(1)).toHaveClass(/assistant/);
  });

  test('04 - Multi-turn conversation', async ({ page }) => {
    await page.goto('/');
    await page.click('#new-chat');
    await expect(page.locator('#chat-form')).toBeVisible();

    // Turn 1.
    await page.fill('#message-input', 'What is Rust?');
    await page.click('#send-btn');
    await page.waitForFunction(() => {
      const bubbles = document.querySelectorAll('.message.assistant .bubble');
      return bubbles.length === 1 && !bubbles[0].classList.contains('streaming');
    }, { timeout: 15000 });

    await page.screenshot({ path: 'screenshots/04a-turn-1.png' });

    // Turn 2.
    await page.fill('#message-input', 'Tell me more about its memory model');
    await page.click('#send-btn');
    await page.waitForFunction(() => {
      const bubbles = document.querySelectorAll('.message.assistant .bubble');
      return bubbles.length === 2 && !bubbles[1].classList.contains('streaming');
    }, { timeout: 15000 });

    await page.screenshot({ path: 'screenshots/04b-turn-2.png' });

    const messages = page.locator('.message');
    await expect(messages).toHaveCount(4);
  });

  test('05 - Multiple sessions in sidebar', async ({ page }) => {
    await page.goto('/');

    // Create first session with a message.
    await page.click('#new-chat');
    await expect(page.locator('#chat-form')).toBeVisible();
    await page.fill('#message-input', 'First chat');
    await page.click('#send-btn');
    await page.waitForFunction(() => {
      const bubbles = document.querySelectorAll('.message.assistant .bubble');
      return bubbles.length === 1 && !bubbles[0].classList.contains('streaming');
    }, { timeout: 15000 });

    // Create second session.
    await page.click('#new-chat');
    await expect(page.locator('.session-item')).toHaveCount(2, { timeout: 5000 });

    await page.screenshot({ path: 'screenshots/05-multiple-sessions.png' });
  });

  test('06 - Switch between sessions', async ({ page }) => {
    await page.goto('/');

    // Create session 1 with a message.
    await page.click('#new-chat');
    await expect(page.locator('#chat-form')).toBeVisible();
    await page.fill('#message-input', 'Hello from session 1');
    await page.click('#send-btn');
    await page.waitForFunction(() => {
      const bubbles = document.querySelectorAll('.message.assistant .bubble');
      return bubbles.length >= 1 && !bubbles[bubbles.length - 1].classList.contains('streaming');
    }, { timeout: 15000 });

    // Create session 2.
    await page.click('#new-chat');
    await expect(page.locator('.session-item')).toHaveCount(2, { timeout: 5000 });
    await page.fill('#message-input', 'Hello from session 2');
    await page.click('#send-btn');
    await page.waitForFunction(() => {
      const bubbles = document.querySelectorAll('.message.assistant .bubble');
      return bubbles.length >= 1 && !bubbles[bubbles.length - 1].classList.contains('streaming');
    }, { timeout: 15000 });

    await page.screenshot({ path: 'screenshots/06a-session-2-active.png' });

    // Click back to session 1 (second item since list is sorted by updated_at desc).
    const sessions = page.locator('.session-item');
    await sessions.nth(1).click();
    await page.waitForTimeout(500);

    await page.screenshot({ path: 'screenshots/06b-switched-to-session-1.png' });

    const userBubble = page.locator('.message.user .bubble').first();
    await expect(userBubble).toContainText('Hello from session 1');
  });

  test('07 - Delete a session', async ({ page }) => {
    await page.goto('/');

    await page.click('#new-chat');
    await expect(page.locator('.session-item')).toHaveCount(1, { timeout: 5000 });

    await page.screenshot({ path: 'screenshots/07a-before-delete.png' });

    // Hover and click delete.
    await page.locator('.session-item').first().hover();
    await page.locator('.session-item .delete-btn').first().click();

    await expect(page.locator('.session-item')).toHaveCount(0, { timeout: 5000 });
    await expect(page.locator('.empty-title')).toBeVisible();

    await page.screenshot({ path: 'screenshots/07b-after-delete.png' });
  });

});
