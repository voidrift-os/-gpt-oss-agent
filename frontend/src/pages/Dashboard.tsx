export default function Dashboard({ onLogout }: { onLogout: () => void }) {
  return <button onClick={onLogout}>Logout</button>;
}
