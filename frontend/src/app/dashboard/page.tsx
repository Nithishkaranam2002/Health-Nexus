import Link from "next/link";
export default function Dashboard() {
  return (
    <div className="container">
      <h2>Dashboard (choose role)</h2>
      <div className="row" style={{marginTop:"1rem"}}>
        <Link className="button" href="/dashboard/clinician">Clinician</Link>
        <Link className="button" href="/dashboard/patient">Patient</Link>
        <Link className="button" href="/dashboard/admin">Admin</Link>
      </div>
    </div>
  );
}
