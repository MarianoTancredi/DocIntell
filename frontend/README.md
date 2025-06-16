# DocIntell Frontend Demo

This is the frontend interface for the DocIntell AI Document Intelligence Platform.

## Quick Start (Demo Mode)

### Prerequisites
- Node.js 18 or higher
- npm (comes with Node.js)

### Running the Frontend

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser and go to:**
   ```
   http://localhost:3000
   ```

## Demo Features

### 🔐 Authentication (Demo Mode)
- **Login**: Use any username and password to log in
- **Registration**: Create a demo account with any credentials
- Data is stored locally in browser storage

### 📊 Dashboard
- View statistics about documents and conversations
- See recent activity with mock data
- Responsive design that works on mobile and desktop

### 🧭 Navigation
- **Dashboard**: Overview and statistics
- **Documents**: Document management interface (UI only)
- **Chat**: Conversational AI interface (UI only)

### 🎨 UI Components
- Material-UI components with modern design
- Dark/light theme support
- Responsive layout for all screen sizes
- Professional typography and spacing

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm run type-check` - Run TypeScript checking
- `npm run format` - Format code with Prettier

## Demo Limitations

This demo runs without a backend, so:
- Authentication is simulated (any credentials work)
- Data is mock/sample data for demonstration
- No actual document processing or AI features
- No real chat functionality

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Main application pages
│   ├── stores/        # State management (Zustand)
│   └── test/          # Test files
├── public/            # Static assets
└── dist/              # Built application (after npm run build)
```

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **Zustand** - State management
- **Vite** - Build tool and dev server
- **React Router** - Navigation

## Customization

To modify the demo data, edit the mock data in:
- `src/pages/DashboardPage.tsx` - Dashboard statistics and lists
- `src/stores/authStore.ts` - Authentication behavior