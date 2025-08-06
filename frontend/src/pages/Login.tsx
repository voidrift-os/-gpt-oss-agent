export default function Login({ onLogin }: { onLogin: () => void }) {
  return <button onClick={onLogin}>Login</button>;
}
