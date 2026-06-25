// Écouteur d'événement déclenché lors de la sélection d'une région
document.getElementById("region").addEventListener("change", async (e) => {
    const regionId = e.target.value;
    const selectDept = document.getElementById("departement");

    // Réinitialisation du menu des départements
    selectDept.innerHTML = '<option value="">-- Choisir --</option>';

    // Arrêt de l'exécution si la sélection est vide
    if (!regionId) return;

    // Appel à l'API pour récupérer la liste des départements correspondants
    const response = await fetch(`${BASE_URL}/api/departements/${regionId}`);
    const depts = await response.json();

    // Remplissage dynamique du menu déroulant avec les données reçues
    for (const dept of depts) {
        const opt = document.createElement("option");
        opt.value = dept.id;
        opt.textContent = `${dept.code} – ${dept.libelle}`;
        selectDept.appendChild(opt);
    }
});