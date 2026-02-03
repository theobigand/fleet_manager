CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'employe',
    nom TEXT,
    prenom TEXT,
    email TEXT,
    actif INTEGER DEFAULT 1
);
            
CREATE TABLE IF NOT EXISTS employes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricule TEXT UNIQUE NOT NULL,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    service TEXT,
    telephone TEXT,
    email TEXT,
    num_permis TEXT,
    date_validite_permis DATE,
    autorise_conduire INTEGER DEFAULT 0,
    photo_path TEXT
);
            
CREATE TABLE IF NOT EXISTS vehicules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    immatriculation TEXT UNIQUE NOT NULL,
    marque TEXT NOT NULL,
    modele TEXT NOT NULL,
    type_vehicule TEXT,
    annee INTEGER,
    date_acquisition DATE,
    kilometrage_actuel INTEGER DEFAULT 0,
    carburant TEXT,
    puissance_fiscale INTEGER,
    numero_chassis TEXT,
    photo_path TEXT,
    type_affectation TEXT DEFAULT 'mutualise',
    statut TEXT DEFAULT 'disponible',
    service_principal TEXT,
    seuil_revision_km INTEGER DEFAULT 15000
);
            
CREATE TABLE IF NOT EXISTS affectations_permanentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER,
    employe_id INTEGER,
    date_debut DATE,
    date_fin DATE,
    FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
    FOREIGN KEY (employe_id) REFERENCES employes(id)
);
            
CREATE TABLE IF NOT EXISTS sorties_reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER,
    employe_id INTEGER,
    date_sortie_prevue DATE,
    heure_sortie_prevue TIME,
    date_retour_prevue DATE,
    heure_retour_prevue TIME,
    date_sortie_reelle DATE,
    heure_sortie_reelle TIME,
    km_depart INTEGER,
    date_retour_reelle DATE,
    heure_retour_reelle TIME,
    km_retour INTEGER,
    motif TEXT,
    destination TEXT,
    etat_retour TEXT,
    niveau_carburant_retour TEXT,
    statut TEXT DEFAULT 'en_cours',
    FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
    FOREIGN KEY (employe_id) REFERENCES employes(id)
);
            
CREATE TABLE IF NOT EXISTS maintenances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER,
    date DATE,
    type_intervention TEXT,
    kilometrage INTEGER,
    cout REAL,
    prestataire TEXT,
    remarques TEXT,
    date_prochaine_echeance DATE,
    FOREIGN KEY (vehicule_id) REFERENCES vehicules(id)
);
            
CREATE TABLE IF NOT EXISTS ravitaillements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER,
    employe_id INTEGER,
    date DATE,
    quantite_litres REAL,
    cout REAL,
    station TEXT,
    kilometrage INTEGER,
    FOREIGN KEY (vehicule_id) REFERENCES vehicules(id),
    FOREIGN KEY (employe_id) REFERENCES employes(id)
);
            
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicule_id INTEGER,
    type_document TEXT,
    date_emission DATE,
    date_echeance DATE,
    chemin_fichier TEXT,
    description TEXT,
    FOREIGN KEY (vehicule_id) REFERENCES vehicules(id)
);
            
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    date_action DATETIME DEFAULT CURRENT_TIMESTAMP,
    details TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);