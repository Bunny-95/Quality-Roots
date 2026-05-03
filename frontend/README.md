# Organic Roots Frontend

AI-enabled agricultural supply chain provenance system frontend application.

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS + shadcn/ui components
- **Routing**: React Router v6
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Notifications**: React Hot Toast
- **QR Codes**: React QR Code + HTML5 QR Code

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/              # Page components
│   │   ├── auth/          # Authentication pages
│   │   ├── farmer/        # Farmer-specific pages
│   │   ├── admin/         # Admin-specific pages
│   │   ├── consumer/      # Consumer pages
│   │   ├── blockchain/    # Blockchain explorer
│   │   └── ai/           # AI analytics pages
│   ├── lib/               # Utilities and API client
│   ├── hooks/             # Custom React hooks
│   ├── types/             # TypeScript type definitions
│   └── styles/            # Global styles
├── public/                # Static assets
└── dist/                  # Build output
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env.local` file in the root:

```env
VITE_API_URL=http://localhost:8000/api
```

## Features

### Authentication
- User registration and login
- Role-based access control (farmer, admin, consumer)
- JWT token management
- Protected routes

### Farmer Dashboard
- Product management
- Batch creation with AI grading
- QR code generation
- Demand forecasting
- Quality insights

### Admin Dashboard
- System overview and statistics
- User management
- Batch monitoring
- Fraud detection analysis
- Quality analytics
- Blockchain verification

### Consumer Verification
- Product verification by batch code
- Complete supply chain journey
- Blockchain integrity check
- Product search and filtering

### Blockchain Explorer
- Complete blockchain visualization
- Block details and verification
- Chain integrity monitoring
- Event tracking

### AI Analytics
- Quality grading insights
- Fraud detection patterns
- Demand forecasting trends
- Model performance metrics

## API Integration

The frontend integrates with the Organic Roots backend API:

- **Base URL**: `http://localhost:8000/api`
- **Authentication**: Bearer token (JWT)
- **QR Codes**: Served from `/qr_codes/`

## Development Guidelines

### Component Structure
- Use TypeScript for all components
- Follow the existing naming conventions
- Keep components small and focused
- Use proper error handling

### Styling
- Use TailwindCSS classes
- Follow the organic color scheme
- Ensure responsive design
- Use shadcn/ui components when possible

### State Management
- Use React Context for global state
- Keep local state in components
- Use custom hooks for complex logic

### API Calls
- Use the centralized API client
- Handle errors gracefully
- Show loading states
- Use toast notifications for feedback

## Deployment

The frontend is designed to be deployed alongside the backend:

```bash
# Build the frontend
npm run build

# The dist/ folder can be served by any static file server
# or integrated with the backend
```

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new components
3. Test thoroughly before committing
4. Update documentation as needed
