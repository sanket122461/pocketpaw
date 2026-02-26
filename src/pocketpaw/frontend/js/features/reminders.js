/**
 * PocketPaw - Reminders Feature Module
 *
 * Created: 2026-02-05
 * Extracted from app.js as part of componentization refactor.
 *
 * Contains reminder-related state and methods:
 * - Reminder CRUD operations
 * - Reminder panel management
 * - Time formatting
 */

window.PocketPaw = window.PocketPaw || {};

window.PocketPaw.Reminders = {
    name: 'Reminders',
    /**
     * Get initial state for Reminders
     */
    getState() {
        return {
            showReminders: false,
            reminders: [],
            reminderInput: '',
            reminderLoading: false,
            _reminderTimerInterval: null
        };
    },

    /**
     * Get methods for Reminders
     */
    getMethods() {
        return {
            /**
             * Handle reminders list
             */
            handleReminders(data) {
                this.reminders = data.reminders || [];
                this.reminderLoading = false;
            },

            /**
             * Handle reminder added
             */
            handleReminderAdded(data) {
                this.reminders.push(data.reminder);
                this.reminderInput = '';
                this.reminderLoading = false;
                this.showToast('Reminder set!', 'success');
            },

            /**
             * Handle reminder deleted
             */
            handleReminderDeleted(data) {
                this.reminders = this.reminders.filter(r => r.id !== data.id);
            },

            /**
             * Handle reminder triggered (notification)
             */
            handleReminderTriggered(data) {
                const reminder = data.reminder;
                this.showToast(`Reminder: ${reminder.text}`, 'info');
                this.addMessage('assistant', `Reminder: ${reminder.text}`);

                // Remove from local list
                this.reminders = this.reminders.filter(r => r.id !== reminder.id);

                // Try desktop notification
                if (Notification.permission === 'granted') {
                    new Notification('PocketPaw Reminder', {
                        body: reminder.text,
                        icon: '/static/icon.png'
                    });
                }
            },

            /**
             * Open reminders panel
             */
            openReminders() {
                this.showReminders = true;
                this.reminderLoading = true;
                socket.send('get_reminders');

                // Request notification permission
                if (Notification.permission === 'default') {
                    Notification.requestPermission();
                }

                // Start the countdown timer
                this.$nextTick(() => {
                    this.startReminderTimer();
                    if (window.refreshIcons) window.refreshIcons();
                });
            },

            /**
             * Add a reminder
             */
            addReminder() {
                const text = this.reminderInput.trim();
                if (!text) return;

                this.reminderLoading = true;
                socket.send('add_reminder', { message: text });
                this.log(`Setting reminder: ${text}`, 'info');
            },

            /**
             * Delete a reminder
             */
            deleteReminder(id) {
                socket.send('delete_reminder', { id });
            },

            /**
             * Format reminder time for display
             */
            formatReminderTime(reminder) {
                const date = new Date(reminder.trigger_at);
                return date.toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            },

            /**
             * Calculate time remaining for a reminder based on trigger_at timestamp
             */
            calculateTimeRemaining(triggerAt) {
                const now = new Date();
                const trigger = new Date(triggerAt);
                const delta = trigger - now;

                if (delta < 0) {
                    return 'past';
                }

                const totalSeconds = Math.floor(delta / 1000);

                if (totalSeconds < 60) {
                    return `in ${totalSeconds}s`;
                } else if (totalSeconds < 3600) {
                    const minutes = Math.floor(totalSeconds / 60);
                    return `in ${minutes}m`;
                } else if (totalSeconds < 86400) {
                    const hours = Math.floor(totalSeconds / 3600);
                    const minutes = Math.floor((totalSeconds % 3600) / 60);
                    return `in ${hours}h ${minutes}m`;
                } else {
                    const days = Math.floor(totalSeconds / 86400);
                    const hours = Math.floor((totalSeconds % 86400) / 3600);
                    return `in ${days}d ${hours}h`;
                }
            },

            /**
             * Update time_remaining for all active reminders
             */
            updateAllReminderTimers() {
                this.reminders.forEach(reminder => {
                    reminder.time_remaining = this.calculateTimeRemaining(reminder.trigger_at);
                });
            },

            /**
             * Start the reminder countdown timer
             */
            startReminderTimer() {
                // Clear any existing timer
                this.stopReminderTimer();

                // Update immediately so there's no delay
                this.updateAllReminderTimers();

                // Update every second
                this._reminderTimerInterval = setInterval(() => {
                    this.updateAllReminderTimers();
                }, 1000);
            },

            /**
             * Stop the reminder countdown timer
             */
            stopReminderTimer() {
                if (this._reminderTimerInterval) {
                    clearInterval(this._reminderTimerInterval);
                    this._reminderTimerInterval = null;
                }
            }
        };
    }
};

window.PocketPaw.Loader.register('Reminders', window.PocketPaw.Reminders);
