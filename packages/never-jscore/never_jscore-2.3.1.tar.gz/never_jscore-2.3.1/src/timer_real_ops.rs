// timer_real_ops.rs - Real async timer implementation for proper Node.js compatibility
//
// This replaces the fake immediate-execution timers with real async timers
// that properly integrate with the event loop.

use deno_core::{extension, op2};
use std::cell::RefCell;
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::sleep;

// Thread-local storage for timer tracking
thread_local! {
    static NEXT_TIMER_ID: RefCell<i32> = RefCell::new(1);
    static ACTIVE_TIMERS: RefCell<HashMap<i32, bool>> = RefCell::new(HashMap::new());
}

// ============================================
// Real setTimeout implementation
// ============================================

#[op2(async)]
/// Real async setTimeout - actually waits for the specified delay
pub async fn op_set_timeout_real(
    #[smi] timer_id: i32,
    #[smi] delay: i32,
) -> bool {
    // Store that this timer is active
    ACTIVE_TIMERS.with(|timers| {
        timers.borrow_mut().insert(timer_id, true);
    });

    // Actually sleep for the delay
    if delay > 0 {
        sleep(Duration::from_millis(delay as u64)).await;
    }

    // Check if timer was cancelled during sleep
    let should_execute = ACTIVE_TIMERS.with(|timers| {
        timers.borrow().get(&timer_id).copied().unwrap_or(false)
    });

    // Clean up
    ACTIVE_TIMERS.with(|timers| {
        timers.borrow_mut().remove(&timer_id);
    });

    should_execute
}

#[op2(fast)]
/// Generate a new timer ID
pub fn op_get_timer_id() -> i32 {
    NEXT_TIMER_ID.with(|next_id| {
        let id = *next_id.borrow();
        *next_id.borrow_mut() += 1;
        id
    })
}

#[op2(fast)]
/// Clear a timer (setTimeout or setInterval)
pub fn op_clear_timer(#[smi] timer_id: i32) {
    ACTIVE_TIMERS.with(|timers| {
        timers.borrow_mut().remove(&timer_id);
    });
}

// ============================================
// Real setInterval implementation
// ============================================

#[op2(async)]
/// Real async setInterval - actually repeats at the specified interval
/// Note: Due to V8 limitations, we only execute once and rely on JS to re-schedule
pub async fn op_set_interval_real(
    #[smi] timer_id: i32,
    #[smi] delay: i32,
) -> bool {
    // Same implementation as setTimeout
    // JS layer handles the re-scheduling

    ACTIVE_TIMERS.with(|timers| {
        timers.borrow_mut().insert(timer_id, true);
    });

    if delay > 0 {
        sleep(Duration::from_millis(delay as u64)).await;
    }

    let should_execute = ACTIVE_TIMERS.with(|timers| {
        timers.borrow().get(&timer_id).copied().unwrap_or(false)
    });

    // Don't clean up for interval - let JS manage it
    should_execute
}

// ============================================
// Extension Definition
// ============================================

extension!(
    timer_real_ops,
    ops = [
        op_set_timeout_real,
        op_set_interval_real,
        op_get_timer_id,
        op_clear_timer,
    ],
);
