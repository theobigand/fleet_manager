import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers import StatsController

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except:
    HAS_MPL = False


class StatisticsView(ctk.CTkFrame):
    def __init__(self, parent, app) -> None:
        super().__init__(parent, fg_color='white')
        self.app = app
        self.ctrl = StatsController()
        self.setup_stats()
        self.refresh()

    def setup_stats(self) -> None:
        # titre
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=20, pady=20)
        ctk.CTkLabel(top, text="Statistiques", font=ctk.CTkFont(size=24, weight='bold'),
                     text_color='#333333').pack(side='left')

        btns = ctk.CTkFrame(top, fg_color='transparent')
        btns.pack(side='right')
        ctk.CTkButton(btns, text="Export CSV", command=self.export_csv,
                      fg_color='#3498db', hover_color='#2980b9', width=100).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Export PDF", command=self.export_pdf,
                      fg_color='#9b59b6', hover_color='#8e44ad', width=100).pack(side='left', padx=5)

        # onglets
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=20, pady=10)

        self.tab_overview()
        self.tab_couts()
        self.tab_usage()
        self.tab_top()

    def tab_overview(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Vue ensemble')

        # cartes stats
        cards = ctk.CTkFrame(tab, fg_color='transparent')
        cards.pack(fill='x', padx=10, pady=10)

        self.card_vehs = self.make_card(cards, "Véhicules", "0", '#3498db')
        self.card_sorties = self.make_card(cards, "Sorties (30j)", "0", '#2ecc71')
        self.card_fuel = self.make_card(cards, "Carburant", "0 €", '#f39c12')
        self.card_maint = self.make_card(cards, "Maintenance", "0 €", '#e74c3c')

        # graphiques
        if HAS_MPL:
            gf = ctk.CTkFrame(tab, fg_color='transparent')
            gf.pack(fill='both', expand=True, padx=10, pady=10)

            self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
            self.fig.patch.set_facecolor('white')
            self.canvas = FigureCanvasTkAgg(self.fig, gf)
            self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def make_card(self, parent, titre, val, color) -> ctk.CTkLabel:
        """Créer une petite carte stat"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.pack(side='left', padx=10, fill='x', expand=True)

        ctk.CTkLabel(card, text=titre, font=ctk.CTkFont(size=12),
                     text_color='white').pack(pady=(10, 5))
        lbl = ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=24, weight='bold'),
                           text_color='white')
        lbl.pack(pady=(5, 10))

        return lbl

    def tab_couts(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Coûts')

        # liste
        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('vehicule', 'carburant', 'maintenance', 'total')
        self.tree_couts = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree_couts.heading('vehicule', text='Véhicule')
        self.tree_couts.heading('carburant', text='Carburant')
        self.tree_couts.heading('maintenance', text='Maintenance')
        self.tree_couts.heading('total', text='Total')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_couts.yview)
        self.tree_couts.configure(yscrollcommand=scrollbar.set)
        self.tree_couts.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # total
        total_f = ctk.CTkFrame(tab, fg_color='#ecf0f1', corner_radius=8)
        total_f.pack(fill='x', padx=10, pady=10)
        self.lbl_total = ctk.CTkLabel(total_f, text="Total: 0 €", font=ctk.CTkFont(size=14, weight='bold'),
                                       text_color='#2c3e50')
        self.lbl_total.pack(pady=10)

    def tab_usage(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Utilisation')

        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('vehicule', 'km', 'sorties', 'jours', 'taux')
        self.tree_usage = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree_usage.heading('vehicule', text='Véhicule')
        self.tree_usage.heading('km', text='Km total')
        self.tree_usage.heading('sorties', text='Sorties')
        self.tree_usage.heading('jours', text='Jours')
        self.tree_usage.heading('taux', text='Taux')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_usage.yview)
        self.tree_usage.configure(yscrollcommand=scrollbar.set)
        self.tree_usage.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def tab_top(self) -> None:
        tab = ctk.CTkFrame(self.tabs, fg_color='white')
        self.tabs.add(tab, text='Top employés')

        tree_frame = ctk.CTkFrame(tab, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        cols = ('rang', 'employe', 'sorties', 'km')
        self.tree_top = ttk.Treeview(tree_frame, columns=cols, show='headings', height=15)
        self.tree_top.heading('rang', text='#')
        self.tree_top.heading('employe', text='Employé')
        self.tree_top.heading('sorties', text='Sorties')
        self.tree_top.heading('km', text='Km total')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree_top.yview)
        self.tree_top.configure(yscrollcommand=scrollbar.set)
        self.tree_top.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def refresh(self) -> None:
        # vue ensemble
        stats = self.ctrl.get_overview()
        self.card_vehs.configure(text=str(stats['total_vehicles']))
        self.card_sorties.configure(text=str(stats['sorties_30j']))
        self.card_fuel.configure(text=f"{stats['cout_carburant_30j']:.0f} €")
        self.card_maint.configure(text=f"{stats['cout_maintenance_30j']:.0f} €")

        # graphiques
        if HAS_MPL:
            self.ax1.clear()
            labels = ['Dispo', 'Sortie', 'Maint', 'Panne']
            sizes = [stats['disponibles'], stats['en_sortie'], stats['en_maintenance'], stats['en_panne']]
            colors = ['#27ae60', '#f39c12', '#3498db', '#e74c3c']

            # enlever les 0
            data = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
            if data:
                l, s, c = zip(*data)
                self.ax1.pie(s, labels=l, colors=c, autopct='%1.0f%%')
            self.ax1.set_title('Statuts véhicules')

            # histogramme
            self.ax2.clear()
            monthly = self.ctrl.get_monthly_costs(6)
            if monthly:
                mois = [m['mois'] for m in monthly]
                carb = [m['carburant'] for m in monthly]
                maint = [m['maintenance'] for m in monthly]

                x = range(len(mois))
                self.ax2.bar([i - 0.2 for i in x], carb, 0.4, label='Carburant', color='orange')
                self.ax2.bar([i + 0.2 for i in x], maint, 0.4, label='Maintenance', color='blue')
                self.ax2.set_xticks(x)
                self.ax2.set_xticklabels(mois, rotation=45)
                self.ax2.legend()
            self.ax2.set_title('Coûts 6 derniers mois')

            self.fig.tight_layout()
            self.canvas.draw()

        # couts
        self.tree_couts.delete(*self.tree_couts.get_children())
        total = 0
        for c in self.ctrl.get_costs_by_vehicle():
            carb = c['carburant'] or 0
            maint = c['maintenance'] or 0
            tot = carb + maint
            total += tot

            self.tree_couts.insert('', 'end',
                                   values=(f"{c['immatriculation']} ({c['marque']})",
                                           f"{carb:.2f} €", f"{maint:.2f} €", f"{tot:.2f} €"))

        self.lbl_total.configure(text=f"Total: {total:.2f} €")

        # usage
        self.tree_usage.delete(*self.tree_usage.get_children())
        for u in self.ctrl.get_usage_by_vehicle():
            km = f"{u['km_actuel']} km" if u['km_actuel'] else '-'
            taux = f"{u['taux_utilisation']:.0f}%" if u.get('taux_utilisation') else '-'

            self.tree_usage.insert('', 'end',
                                   values=(f"{u['immatriculation']} ({u['marque']})",
                                           km, u['sorties_30j'], u['jours_utilises'], taux))

        # top
        self.tree_top.delete(*self.tree_top.get_children())
        for i, e in enumerate(self.ctrl.get_top_employees(10), 1):
            km = f"{e['km_total']} km" if e['km_total'] else '0 km'
            self.tree_top.insert('', 'end',
                                 values=(f"#{i}", f"{e['prenom']} {e['nom']}", e['nb_sorties'], km))

    def export_csv(self) -> None:
        try:
            path = self.ctrl.export_csv(self.app.current_user.id)
            messagebox.showinfo("Export", f"Fichier créé:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def export_pdf(self) -> None:
        try:
            path = self.ctrl.export_pdf(self.app.current_user.id)
            messagebox.showinfo("Export", f"Fichier créé:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))