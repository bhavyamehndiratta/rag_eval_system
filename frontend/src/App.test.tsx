import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders the app title and all three tabs', () => {
  render(<App />);
  expect(screen.getByText('RAG Eval System')).toBeInTheDocument();
  // 'Ask' appears twice: the tab and the submit button.
  expect(screen.getAllByRole('button', { name: 'Ask' })).toHaveLength(2);
  expect(screen.getByRole('button', { name: 'Evaluate' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'History' })).toBeInTheDocument();
});

test('defaults to the hybrid retrieval strategy', () => {
  render(<App />);
  expect(screen.getByRole('combobox')).toHaveValue('hybrid');
});

test('switches to the evaluate tab', () => {
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Evaluate' }));
  expect(screen.getByRole('button', { name: 'Run Evaluation' })).toBeInTheDocument();
});
