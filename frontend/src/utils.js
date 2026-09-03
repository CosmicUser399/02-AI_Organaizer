/**
 * Shared utility functions for formatting and display logic.
 */

/**
 * Format a due date as a relative human-readable Russian string.
 *
 * Examples: "сегодня 14:00", "завтра 09:30", "5 дней назад".
 * Returns null if isoString is falsy.
 */
export function formatDue(isoString) {
    if (!isoString) return null;

    const date = new Date(isoString);
    const now = new Date();
    const todayStart = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
    );
    const dateStart = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate(),
    );

    const diffDays = Math.round(
        (dateStart - todayStart) / (1000 * 60 * 60 * 24),
    );
    const timeStr = date.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit',
    });

    if (diffDays === 0) return `сегодня ${timeStr}`;
    if (diffDays === 1) return `завтра ${timeStr}`;
    if (diffDays === -1) return `вчера ${timeStr}`;
    if (diffDays < 0) return `${Math.abs(diffDays)} дн. назад`;
    return `через ${diffDays} дн., ${timeStr}`;
}

/**
 * Format a date as a short locale string, e.g. "15 сен. 2026 г.".
 * Returns empty string if isoString is falsy.
 */
export function formatDate(isoString) {
    if (!isoString) return '';
    return new Date(isoString).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    });
}

/**
 * Return MUI color name for a task based on urgency and importance.
 *
 * Mapping:
 *   urgent + important → 'error'   (red)
 *   urgent only        → 'warning' (amber)
 *   important only     → 'primary' (indigo)
 *   neither            → 'default' (grey)
 */
export function getPriorityColor(isUrgent, isImportant) {
    if (isUrgent && isImportant) return 'error';
    if (isUrgent) return 'warning';
    if (isImportant) return 'primary';
    return 'default';
}
