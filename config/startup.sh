#!/bin/bash

# Start tmux session with custom layout
#Project: 
PROJECT_NAME="cp"

# # Source environment vars 
# set -a # automatically export all variables
# source ./config/.env
# set +a # stop automatically exporting

# # Remove existing connections
# rm ~/.local/share/db_ui/connections.json > /dev/null 2>&1

# Try to attach by default
tmux a -t "${PROJECT_NAME} > /dev/null 2>&1"

# If the prior process fails, setup new:
if [ $? -ne 0 ]; then
    tmux new-session -d -s "${PROJECT_NAME}" > /dev/null 2>&1

    # Window 1: Python IDE
    WINDOW_1_NAME="main"
    REPL_TARGET="python3"
    TARGET_FILE_PATH="./src/sync_vs_async_requests.py"
    EXECUTION_TARGET="python3 -m pdb ${TARGET_FILE_PATH}"

    # Rename the first window
    tmux rename-window "${WINDOW_1_NAME}"

    # Setup the first window with a vertical split and specific commands
    tmux split-window -v
    
    # Create main neovim window inside venv
    tmux resize-pane -t "${PROJECT_NAME}:${WINDOW_1_NAME}.0" -D 10
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.0" 'source venv/bin/activate' C-m
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.0" "nvim ${TARGET_FILE_PATH}" C-m
   
    # Create python3 repl window inside venv
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.1" 'source venv/bin/activate' C-m
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.1" "clear && ${REPL_TARGET}" C-m

    # Create python3 execution window inside venv
    tmux select-pane -t "${PROJECT_NAME}:${WINDOW_1_NAME}.1"
    tmux split-pane -h
    tmux resize-pane -t "${PROJECT_NAME}:${WINDOW_1_NAME}.1" -R 10
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.2" 'source venv/bin/activate' C-m
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.2" 'clear' C-m
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_1_NAME}.2" "${EXECUTION_TARGET}" # Don't press enter to send command
    tmux select-pane -t "${PROJECT_NAME}:${WINDOW_1_NAME}.1" # Reselect the REPL pane to store as {last} target in vim-slime

    # # Window 2: SQL IDE
    # WINDOW_2_NAME="sql"
    # SQL_CONNECTION_NAME="HawkWatch"
    # TARGET_SQL_FILE_PATH="./src/exploration/test_queries.sql"
    # DOTENV_PATH="./config"
    # # Connection added with dadbod-ui's vim-dotenv support, need to be in same directory as .env file
    # ln -s "${TARGET_SQL_FILE_PATH}" "${DOTENV_PATH}/.tmux_setup_working_file.sql"
    # tmux new-window -t "${PROJECT_NAME}" -n "${WINDOW_2_NAME}"
    # tmux send-keys -t "${PROJECT_NAME}:${WINDOW_2_NAME}" "nvim ${DOTENV_PATH}/.tmux_setup_working_file.sql" C-m
    # tmux send-keys -t "${PROJECT_NAME}:${WINDOW_2_NAME}" ':DBUIFindBuffer' C-m

    # Window 3: Git Workflow
    WINDOW_3_NAME="git"
    GH_USER_NAME="adamosmi"
    tmux new-window -t "${PROJECT_NAME}" -n "${WINDOW_3_NAME}"
    gh auth switch -u "${GH_USER_NAME}"
    tmux send-keys -t "${PROJECT_NAME}:${WINDOW_3_NAME}" 'lazygit' C-m

    # Attach to session
    tmux select-window -t "${PROJECT_NAME}:${WINDOW_1_NAME}"
    tmux select-pane -t "${PROJECT_NAME}:${WINDOW_1_NAME}.0"
    tmux attach -t "${PROJECT_NAME}" > /dev/null 2>&1
fi
