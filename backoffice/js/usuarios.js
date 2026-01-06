async function cargarUsuarios() {
    const res = await fetch("/admin/usuarios", {
        headers: { Authorization: "Bearer " + token }
    });

    const usuarios = await res.json();
    const tbody = document.getElementById("tablaUsuarios");
    tbody.innerHTML = "";

    usuarios.forEach(u => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${u.id}</td>
            <td>${u.username}</td>
            <td>${u.email ?? ""}</td>
            <td>${u.estado}</td>
            <td>
                <button class="btn btn-sm btn-warning me-1"
                    onclick="cambiarEstado(${u.id}, '${u.estado === 'ACTIVO' ? 'BLOQUEADO' : 'ACTIVO'}')">
                    ${u.estado === 'ACTIVO' ? 'Bloquear' : 'Activar'}
                </button>

                <button class="btn btn-sm btn-info"
                    onclick="editarUsuario(${u.id})">
                    Editar
                </button>


                <button class="btn btn-sm btn-danger"
                    onclick="eliminarUsuario(${u.id})">
                    Eliminar
                </button>

                <button class="btn btn-sm btn-secondary"
                    onclick="resetPin(${u.id})">
                    Reset PIN
                </button>

            </td>

        `;
        tbody.appendChild(tr);
    });
}

function mostrarUsuarios() {
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("usuariosBox").style.display = "block";

    document.querySelectorAll(".nav-link").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".nav-link")[1].classList.add("active");

    cargarUsuarios();
}

async function cambiarEstado(id, estado) {
    await fetch(`/admin/usuarios/${id}/estado?estado=${estado}`, {
        method: "PATCH",
        headers: { Authorization: "Bearer " + token }
    });

    cargarUsuarios();
    cargarDashboard();
}


async function editarUsuario(id) {
    const nuevoEmail = prompt("Nuevo email:");

    if (!nuevoEmail) return;

    await fetch(`/admin/usuarios/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ email: nuevoEmail })
    });

    cargarUsuarios();
}


async function eliminarUsuario(id) {
    if (!confirm("¿Seguro que deseas eliminar este usuario?")) return;

    await fetch(`/admin/usuarios/${id}`, {
        method: "DELETE",
        headers: { "Authorization": "Bearer " + token }
    });

    cargarUsuarios();
    cargarDashboard();
}

async function resetPin(id) {
    const nuevoPin = prompt("Ingrese nuevo PIN (mín. 4 dígitos):");

    if (!nuevoPin || nuevoPin.length < 4) {
        alert("PIN inválido");
        return;
    }

    const res = await fetch(`/admin/usuarios/${id}/reset_pin?nuevo_pin=${nuevoPin}`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    if (!res.ok) {
        alert("Error al resetear PIN");
        return;
    }

    alert("PIN actualizado correctamente");
}
