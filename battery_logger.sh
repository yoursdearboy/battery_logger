#!/bin/sh

# ask for input with default answer
# $1 - message
# $2 - default answer (empty if no provided)
ask_for_input() {
    cmd="display dialog \"$1\" default answer \"$2\""
    osascript -e "$cmd" | sed "s/.*text returned://"
}

# display alert
# $1 - title
# $2 - optional message
display_alert() {
    cmd="display alert \"$1\""
    if [ -n "$2" ]; then
        cmd="$cmd message \"$2\""
    fi
    osascript -e "$cmd" > /dev/null
}

# Load settings
SETTINGS_PATH="$HOME/.battery_logger"

load_settings() {
    if [ -f "$SETTINGS_PATH" ]; then
        source $SETTINGS_PATH
    fi
}

save_settings() {
    printf "%s\n" \
        "LOG_PATH=\"$LOG_PATH\"" \
        "TIMEOUT=\"$TIMEOUT\"" > $SETTINGS_PATH
}

load_settings

# If no settings, configure the program
if [ -z "$LOG_PATH" ] || [ -z "$TIMEOUT" ]; then
    LOG_PATH=$(ask_for_input "Battery log file path" "$HOME/.battery.log")
    TIMEOUT=$(ask_for_input "Timeout" "60s")

    if [ -z "$LOG_PATH" ] || [ -z "$TIMEOUT" ]; then
        display_alert "Error" "Wrong log file path or timeout"
        exit 1
    fi

    save_settings

    display_alert "Battery logger started" "$(printf "%s\n" \
        "Settings are in $SETTINGS_PATH" \
        "Stop the logger using pkill -9 -f Battery Logger.app")"
fi

# The logger
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

workload() {
    ioreg -r -c AppleSmartBattery | tail -n +2
}

separator() {
    : # no separator needed
}

while true; do
    timestamp >> $LOG_PATH
    workload >> $LOG_PATH
    separator >> $LOG_PATH
    sleep $TIMEOUT
done
