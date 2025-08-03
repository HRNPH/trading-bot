import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./index.css";

import Dashboard from "./components/Dashboard";
import Navigation from "./components/Navigation";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
