# Trading Bot Frontend

Modern React frontend for the Trading Bot Platform using Vite, Tailwind CSS, Recharts, and shadcn/ui.

## Features

- 🎨 **Modern UI**: Built with Tailwind CSS and shadcn/ui components
- 📊 **Beautiful Charts**: Powered by Recharts for data visualization
- ⚡ **Real-time Updates**: Live trading status and portfolio updates
- 🔧 **TypeScript**: Full type safety and better developer experience
- 📱 **Responsive**: Works perfectly on desktop and mobile devices
- ⚡ **Fast Development**: Vite for lightning-fast hot module replacement

## Tech Stack

- **React 18** - Modern React with hooks
- **TypeScript** - Type safety and better DX
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible component library
- **Recharts** - Composable charting library
- **Lucide React** - Beautiful icons
- **React Router** - Client-side routing

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm (recommended) or npm
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:

```bash
pnpm install
```

2. Start the development server:

```bash
pnpm dev
```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   ├── Dashboard.tsx # Main dashboard component
│   │   └── Navigation.tsx
│   ├── hooks/
│   │   └── useApi.ts     # Custom API hook
│   ├── lib/
│   │   └── utils.ts      # Utility functions
│   ├── types/
│   │   └── index.ts      # TypeScript types
│   ├── App.tsx
│   ├── main.tsx          # Vite entry point
│   └── index.css         # Tailwind CSS
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json
```

## Development

### Adding New Components

1. Create new components in `src/components/`
2. Use shadcn/ui components from `src/components/ui/`
3. Style with Tailwind CSS classes

### API Integration

- Use the `useApi` hook for data fetching
- API endpoints are configured to proxy to the backend via Vite
- All API calls are typed with TypeScript

### Styling

- Use Tailwind CSS utility classes
- Follow the design system defined in `tailwind.config.js`
- Use shadcn/ui components for consistent UI

## Building for Production

```bash
pnpm build
```

This creates an optimized production build in the `dist` folder.

## Preview Production Build

```bash
pnpm preview
```

This serves the production build locally for testing.

## Deployment

The frontend can be deployed to any static hosting service:

- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront

Make sure to configure the API proxy or update the API endpoints for production.

## Vite Configuration

The project uses Vite for:

- **Fast Development**: Hot module replacement
- **TypeScript Support**: Built-in TypeScript compilation
- **API Proxy**: Automatic proxy to backend during development
- **Path Aliases**: `@/` maps to `src/` directory
