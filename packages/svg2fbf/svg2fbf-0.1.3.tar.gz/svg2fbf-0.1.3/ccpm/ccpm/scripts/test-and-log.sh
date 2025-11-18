#!/bin/bash

# Script to run tests with automatic log redirection
# Supports multiple languages and test frameworks
# Adapts to project-specific test structures (e.g., session-based E2E tests)
#
# Features:
#   - Auto-detects session-based tests (tests/sessions/test_session_NNN_Mframes/)
#   - Creates timestamped run directories for session tests
#   - Reads pytest options from pyproject.toml ([tool.pytest.ini_options])
#   - Falls back to standard tests/logs/ for conventional tests
#
# Usage: ./claude/scripts/test-and-log.sh path/to/test.[ext] [optional_log_name.log]

if [ $# -eq 0 ]; then
    echo "Usage: $0 <test_file_path> [log_filename]"
    echo "Examples:"
    echo "  $0 tests/e2e/my_test_name.py                    # Python pytest"
    echo "  $0 tests/unit/my_test.js                        # JavaScript Jest/Mocha"
    echo "  $0 tests/sessions/test_session_014_35frames/    # Session-based test"
    echo "  $0 src/test/java/MyTest.java                    # Java JUnit"
    echo "  $0 tests/MyTest.cs                              # C# MSTest/NUnit"
    echo "  $0 tests/my_test.rb                             # Ruby RSpec"
    echo "  $0 tests/my_test_name.py my_test_name_v2.log    # Custom log name"
    exit 1
fi

TEST_PATH="$1"

# Detect session-based test structure (e.g., svg2fbf pattern)
# Pattern: tests/sessions/test_session_NNN_Mframes/
if [[ "$TEST_PATH" =~ tests/sessions/test_session_[0-9]+_[0-9]+frames ]]; then
    SESSION_BASED_TEST=true
    # Extract session directory
    SESSION_DIR=$(echo "$TEST_PATH" | grep -o 'tests/sessions/test_session_[0-9]*_[0-9]*frames')
    # Create timestamped run directory within session
    TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
    LOG_DIR="${SESSION_DIR}/runs/${TIMESTAMP}"
    mkdir -p "$LOG_DIR"
    LOG_FILE="${LOG_DIR}/test.log"
    echo "📁 Session-based test detected"
    echo "   Session: $SESSION_DIR"
    echo "   Run directory: $LOG_DIR"
else
    SESSION_BASED_TEST=false
    # Standard log directory
    mkdir -p tests/logs

    # Determine log file name
    if [ $# -ge 2 ]; then
        # Use provided log filename (second parameter)
        LOG_NAME="$2"
        # Ensure it ends with .log
        if [[ ! "$LOG_NAME" == *.log ]]; then
            LOG_NAME="${LOG_NAME}.log"
        fi
        LOG_FILE="tests/logs/${LOG_NAME}"
    else
        # Extract the test filename without extension for the log name
        TEST_NAME=$(basename "$TEST_PATH")
        TEST_NAME=${TEST_NAME%.*}  # Remove extension regardless of what it is
        LOG_FILE="tests/logs/${TEST_NAME}.log"
    fi
fi

# Detect test framework and run appropriate command
echo "Running test: $TEST_PATH"
echo "Logging to: $LOG_FILE"

# Determine test command based on file extension and project structure
if [[ "$TEST_PATH" =~ \.py$ ]]; then
    # Python - try pytest first, fallback to python
    if command -v pytest >/dev/null 2>&1; then
        # Check for pytest options in pyproject.toml
        PYTEST_OPTS="-v"
        if [ -f "pyproject.toml" ]; then
            # Extract custom pytest options from pyproject.toml
            # This handles multi-line addopts in [tool.pytest.ini_options]
            CUSTOM_OPTS=$(python3 -c "
import tomllib
try:
    with open('pyproject.toml', 'rb') as f:
        config = tomllib.load(f)
    pytest_opts = config.get('tool', {}).get('pytest', {}).get('ini_options', {}).get('addopts', '')
    if pytest_opts:
        # Clean up multi-line string and extra whitespace
        opts = ' '.join(pytest_opts.split())
        print(opts)
except:
    pass
" 2>/dev/null)

            if [ -n "$CUSTOM_OPTS" ]; then
                PYTEST_OPTS="$CUSTOM_OPTS"
                echo "📋 Using pytest options from pyproject.toml: $PYTEST_OPTS"
            fi
        fi

        pytest "$TEST_PATH" $PYTEST_OPTS > "$LOG_FILE" 2>&1
    else
        python "$TEST_PATH" > "$LOG_FILE" 2>&1
    fi
elif [[ "$TEST_PATH" =~ \.(js|ts)$ ]]; then
    # JavaScript/TypeScript - try npm test, then jest, then node
    if [ -f package.json ] && grep -q "test" package.json; then
        npm test "$TEST_PATH" > "$LOG_FILE" 2>&1
    elif command -v jest >/dev/null 2>&1; then
        jest "$TEST_PATH" > "$LOG_FILE" 2>&1
    else
        node "$TEST_PATH" > "$LOG_FILE" 2>&1
    fi
elif [[ "$TEST_PATH" =~ \.java$ ]]; then
    # Java - try Maven, then Gradle
    if [ -f pom.xml ]; then
        mvn test -Dtest="$(basename "$TEST_PATH" .java)" > "$LOG_FILE" 2>&1
    elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
        ./gradlew test --tests "$(basename "$TEST_PATH" .java)" > "$LOG_FILE" 2>&1
    else
        echo "❌ Java test runner not found (need Maven or Gradle)" > "$LOG_FILE" 2>&1
        exit 1
    fi
elif [[ "$TEST_PATH" =~ \.cs$ ]]; then
    # C# .NET
    dotnet test "$TEST_PATH" > "$LOG_FILE" 2>&1
elif [[ "$TEST_PATH" =~ \.rb$ ]]; then
    # Ruby - try bundle exec rspec, then rspec
    if [ -f Gemfile ]; then
        bundle exec rspec "$TEST_PATH" > "$LOG_FILE" 2>&1
    elif command -v rspec >/dev/null 2>&1; then
        rspec "$TEST_PATH" > "$LOG_FILE" 2>&1
    else
        ruby "$TEST_PATH" > "$LOG_FILE" 2>&1
    fi
elif [[ "$TEST_PATH" =~ \.php$ ]]; then
    # PHP - try PHPUnit
    if [ -f vendor/bin/phpunit ]; then
        ./vendor/bin/phpunit "$TEST_PATH" > "$LOG_FILE" 2>&1
    elif command -v phpunit >/dev/null 2>&1; then
        phpunit "$TEST_PATH" > "$LOG_FILE" 2>&1
    else
        php "$TEST_PATH" > "$LOG_FILE" 2>&1
    fi
elif [[ "$TEST_PATH" =~ \.go$ ]]; then
    # Go
    go test "$(dirname "$TEST_PATH")" -v > "$LOG_FILE" 2>&1
elif [[ "$TEST_PATH" =~ \.rs$ ]]; then
    # Rust
    cargo test "$(basename "$TEST_PATH" .rs)" > "$LOG_FILE" 2>&1
elif [[ "$TEST_PATH" =~ \.swift$ ]]; then
    # Swift
    swift test > "$LOG_FILE" 2>&1
elif [[ "$TEST_PATH" =~ \.dart$ ]]; then
    # Dart/Flutter
    if [ -f pubspec.yaml ]; then
        flutter test "$TEST_PATH" > "$LOG_FILE" 2>&1
    else
        dart test "$TEST_PATH" > "$LOG_FILE" 2>&1
    fi
else
    echo "❌ Unsupported test file type: $TEST_PATH" > "$LOG_FILE" 2>&1
    echo "❌ Unsupported test file type: $TEST_PATH"
    exit 1
fi

# Check exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Test completed successfully. Log saved to $LOG_FILE"
else
    echo "❌ Test failed with exit code $EXIT_CODE. Check $LOG_FILE for details"
fi

exit $EXIT_CODE
