#!/bin/bash

# Organic Roots - Unified Startup Script
# Starts both backend and frontend services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Organic Roots Startup Script${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for service at $url to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_status "Service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Service failed to start within expected time"
    return 1
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    # Check if Python is installed
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "backend/main.py" ]; then
        print_error "backend/main.py not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check if backend port is in use
    if port_in_use 8000; then
        print_warning "Port 8000 is already in use. Trying to kill existing process..."
        pkill -f "uvicorn.*main:app" || true
        sleep 2
        
        if port_in_use 8000; then
            print_error "Could not free port 8000. Please manually stop the service."
            exit 1
        fi
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "backend/venv" ]; then
        print_status "Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        cd ..
    fi
    
    # Activate virtual environment and install dependencies
    print_status "Installing backend dependencies..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Start backend in background
    print_status "Starting FastAPI server..."
    cd backend
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to be ready
    if wait_for_service "http://localhost:8000"; then
        print_status "Backend server started successfully (PID: $BACKEND_PID)"
        echo $BACKEND_PID > backend.pid
    else
        print_error "Backend server failed to start"
        if [ -f "backend.log" ]; then
            print_error "Check backend.log for details:"
            tail -10 backend.log
        fi
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    # Check if Node.js is installed
    if ! command_exists node; then
        print_error "Node.js is not installed"
        exit 1
    fi
    
    # Check if npm is installed
    if ! command_exists npm; then
        print_error "npm is not installed"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "frontend/package.json" ]; then
        print_error "frontend/package.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # Check if frontend port is in use
    if port_in_use 5173; then
        print_warning "Port 5173 is already in use. Trying to kill existing process..."
        pkill -f "vite" || true
        sleep 2
        
        if port_in_use 5173; then
            print_error "Could not free port 5173. Please manually stop the service."
            exit 1
        fi
    fi
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    # Start frontend in background
    print_status "Starting Vite dev server..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to be ready
    if wait_for_service "http://localhost:5173"; then
        print_status "Frontend server started successfully (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > frontend.pid
    else
        print_error "Frontend server failed to start"
        if [ -f "frontend.log" ]; then
            print_error "Check frontend.log for details:"
            tail -10 frontend.log
        fi
        exit 1
    fi
}

# Function to run integration tests
run_tests() {
    print_status "Running integration tests..."
    
    if [ ! -f "test_integration.py" ]; then
        print_error "Integration test script not found"
        return 1
    fi
    
    python3 test_integration.py
    return $?
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_status "Backend server stopped"
        fi
        rm -f backend.pid
    fi
    
    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_status "Frontend server stopped"
        fi
        rm -f frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn.*main:app" || true
    pkill -f "vite" || true
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start     Start both backend and frontend services"
    echo "  backend   Start only backend service"
    echo "  frontend  Start only frontend service"
    echo "  stop      Stop all services"
    echo "  test      Run integration tests"
    echo "  restart   Restart all services"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start both services"
    echo "  $0 backend    # Start only backend"
    echo "  $0 test       # Run tests"
}

# Function to show status
show_status() {
    print_status "Checking service status..."
    
    # Check backend
    if port_in_use 8000; then
        print_status "Backend server is running on port 8000"
    else
        print_warning "Backend server is not running"
    fi
    
    # Check frontend
    if port_in_use 5173; then
        print_status "Frontend server is running on port 5173"
    else
        print_warning "Frontend server is not running"
    fi
    
    # Show PIDs if available
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        print_status "Backend PID: $BACKEND_PID"
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        print_status "Frontend PID: $FRONTEND_PID"
    fi
}

# Main script logic
case "${1:-start}" in
    "start")
        print_header
        start_backend
        start_frontend
        print_status "Both services started successfully!"
        echo ""
        print_status "🌐 Frontend: http://localhost:5173"
        print_status "🔧 Backend API: http://localhost:8000"
        print_status "📚 API Docs: http://localhost:8000/docs"
        echo ""
        print_status "Use '$0 stop' to stop all services"
        print_status "Use '$0 status' to check service status"
        print_status "Use '$0 test' to run integration tests"
        ;;
    
    "backend")
        print_header
        start_backend
        print_status "Backend started successfully!"
        echo ""
        print_status "🔧 Backend API: http://localhost:8000"
        print_status "📚 API Docs: http://localhost:8000/docs"
        ;;
    
    "frontend")
        print_header
        start_frontend
        print_status "Frontend started successfully!"
        echo ""
        print_status "🌐 Frontend: http://localhost:5173"
        ;;
    
    "stop")
        print_header
        stop_services
        print_status "All services stopped"
        ;;
    
    "restart")
        print_header
        stop_services
        sleep 2
        start_backend
        start_frontend
        print_status "Services restarted successfully!"
        ;;
    
    "test")
        print_header
        run_tests
        ;;
    
    "status")
        print_header
        show_status
        ;;
    
    "help"|"-h"|"--help")
        show_help
        ;;
    
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
