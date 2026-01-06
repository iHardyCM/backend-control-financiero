async function cargarDashboard() {
    const res = await fetch("/admin/dashboard", {
        headers: { Authorization: "Bearer " + token }
    });

    if (!res.ok) return;

    const d = await res.json();

    document.getElementById("dashboard").innerHTML = `
        <div class="col">
            <div class="alert alert-primary">👥 Total usuarios: <b>${d.total_usuarios}</b></div>
        </div>
        <div class="col">
            <div class="alert alert-success">✅ Activos: <b>${d.usuarios_activos}</b></div>
        </div>
        <div class="col">
            <div class="alert alert-danger">⛔ Bloqueados: <b>${d.usuarios_bloqueados}</b></div>
        </div>
    `;
}

function mostrarDashboard() {
    document.getElementById("dashboard").style.display = "flex";
    document.getElementById("usuariosBox").style.display = "none";

    document.querySelectorAll(".nav-link").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".nav-link")[0].classList.add("active");

    cargarDashboard();
}
