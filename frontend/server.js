import { handler } from './build/handler.js';
import express from 'express';

const app = express();
const port = process.env.PORT || 3000;

// Optional: Add compression middleware
import compression from 'compression';
app.use(compression());

// Optional: Serve static files
app.use(express.static('build/client'));

// Let SvelteKit handle everything else
app.use(handler);

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
}); 