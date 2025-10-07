import WorkflowEditor from '../components/WorkflowEditor';

export default function Home() {
  return (
    <div>
      <header style={{ textAlign: 'center', padding: '20px' }}>
        <h1>NeuroGrid - AI Workflow Platform</h1>
      </header>
      <main>
        <WorkflowEditor />
      </main>
    </div>
  );
}