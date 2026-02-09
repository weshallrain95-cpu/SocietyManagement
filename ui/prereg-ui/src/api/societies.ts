export async function fetchSocieties() {
  const res = await fetch("http://127.0.0.1:8000/api/societies");

  if (!res.ok) {
    throw new Error("Failed to load societies");
  }

  return res.json();
}
