import { spawn } from 'child_process';

console.log('Starting Flask application...');

// Create a child process to run the Flask app
const flaskProcess = spawn('python', ['run.py'], {
  stdio: 'inherit'
});

// Handle process exit
flaskProcess.on('close', (code) => {
  console.log(`Flask process exited with code ${code}`);
  process.exit(code);
});

// Handle errors
flaskProcess.on('error', (err) => {
  console.error('Failed to start Flask process:', err);
  process.exit(1);
});

// Handle SIGINT (Ctrl+C) to properly terminate the Flask process
process.on('SIGINT', () => {
  console.log('Received SIGINT. Shutting down Flask server...');
  flaskProcess.kill('SIGINT');
  process.exit(0);
});