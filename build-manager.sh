#!/bin/bash

# Universal Soul AI - Build Manager
# Manages switching between minimal and full APK builds

set -e

echo "🚀 Universal Soul AI - Build Manager"
echo "==================================="

# Function to enable a workflow
enable_workflow() {
    local workflow_name=$1
    local disabled_name="${workflow_name}.disabled"
    
    if [ -f ".github/workflows/${disabled_name}" ]; then
        mv ".github/workflows/${disabled_name}" ".github/workflows/${workflow_name}"
        echo "✅ Enabled: ${workflow_name}"
    elif [ -f ".github/workflows/${workflow_name}" ]; then
        echo "ℹ️  Already enabled: ${workflow_name}"
    else
        echo "❌ Workflow not found: ${workflow_name}"
        return 1
    fi
}

# Function to disable a workflow
disable_workflow() {
    local workflow_name=$1
    local disabled_name="${workflow_name}.disabled"
    
    if [ -f ".github/workflows/${workflow_name}" ]; then
        mv ".github/workflows/${workflow_name}" ".github/workflows/${disabled_name}"
        echo "🔇 Disabled: ${workflow_name}"
    elif [ -f ".github/workflows/${disabled_name}" ]; then
        echo "ℹ️  Already disabled: ${workflow_name}"
    else
        echo "❌ Workflow not found: ${workflow_name}"
        return 1
    fi
}

# Function to show current status
show_status() {
    echo ""
    echo "📊 Current Workflow Status:"
    echo "=========================="
    
    for workflow in build-minimal.yml build-full.yml build-apk.yml build-apk-simple.yml; do
        if [ -f ".github/workflows/${workflow}" ]; then
            echo "✅ ACTIVE:   ${workflow}"
        elif [ -f ".github/workflows/${workflow}.disabled" ]; then
            echo "🔇 DISABLED: ${workflow}"
        else
            echo "❓ MISSING:  ${workflow}"
        fi
    done
    echo ""
}

# Function to switch to minimal build
enable_minimal() {
    echo "🔄 Switching to MINIMAL build mode..."
    enable_workflow "build-minimal.yml"
    disable_workflow "build-full.yml"
    disable_workflow "build-apk.yml"
    disable_workflow "build-apk-simple.yml"
    echo "✅ Minimal build mode activated"
}

# Function to switch to full build
enable_full() {
    echo "🔄 Switching to FULL build mode..."
    enable_workflow "build-full.yml"
    disable_workflow "build-minimal.yml"
    disable_workflow "build-apk.yml"
    disable_workflow "build-apk-simple.yml"
    echo "✅ Full build mode activated"
}

# Function to enable all workflows
enable_all() {
    echo "🔄 Enabling ALL workflows..."
    enable_workflow "build-minimal.yml"
    enable_workflow "build-full.yml"
    enable_workflow "build-apk.yml"
    enable_workflow "build-apk-simple.yml"
    echo "✅ All workflows activated"
}

# Function to disable all workflows
disable_all() {
    echo "🔄 Disabling ALL workflows..."
    disable_workflow "build-minimal.yml"
    disable_workflow "build-full.yml"
    disable_workflow "build-apk.yml"
    disable_workflow "build-apk-simple.yml"
    echo "✅ All workflows disabled"
}

# Parse command line arguments
case "${1:-status}" in
    "minimal"|"min")
        enable_minimal
        ;;
    "full"|"complete")
        enable_full
        ;;
    "all"|"enable-all")
        enable_all
        ;;
    "none"|"disable-all")
        disable_all
        ;;
    "status"|"show"|"")
        show_status
        ;;
    "help"|"-h"|"--help")
        echo ""
        echo "📚 Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  minimal     Enable only minimal build workflow"
        echo "  full        Enable only full-featured build workflow"
        echo "  all         Enable all build workflows"
        echo "  none        Disable all build workflows"
        echo "  status      Show current workflow status (default)"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 minimal    # Switch to minimal APK builds"
        echo "  $0 full       # Switch to full-featured APK builds"
        echo "  $0 status     # Check which workflows are active"
        echo ""
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

show_status

if command -v git >/dev/null 2>&1; then
    if [ -n "$(git status --porcelain)" ]; then
        echo "💡 Don't forget to commit and push your workflow changes!"
        echo "   git add .github/workflows/"
        echo "   git commit -m \"Switch build workflow configuration\""
        echo "   git push"
    fi
fi