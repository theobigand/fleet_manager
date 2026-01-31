# views/statistics.py - Statistiques (MVC)
import tkinter as tk
from tkinter import ttk, messagebox

from controllers import StatsController
from widgets import FilterableTreeview, StatCard

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class StatisticsView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.controller = StatsController()
        self.configure(bg='#ffffff')
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        header = tk.Frame(self, bg='#ffffff')
        header.pack(fill='x', padx=20, pady=(20, 10))
        tk.Label(header, text="Statistiques", font=('Helvetica', 18, 'bold'), bg='#ffffff', fg='#000000').pack(side='left')
        btn = tk.Frame(header, bg='#ffffff')
        btn.pack(side='right')
        tk.Button(btn, text="CSV", command=self._export_csv, bg='#3498db', fg='#000000', relief='flat').pack(side='left', padx=2)
        tk.Button(btn, text="PDF", command=self._export_pdf, bg='#9b59b6', fg='#000000', relief='flat').pack(side='left', padx=2)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Overview
        f1 = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(f1, text='Vue d\'ensemble')
        cards = tk.Frame(f1, bg='#ffffff')
        cards.pack(fill='x', padx=10, pady=10)
        self.card_veh = StatCard(cards, "Véhicules", "0", '#337ab7')
        self.card_veh.pack(side='left', padx=10, expand=True, fill='x')
        self.card_sort = StatCard(cards, "Sorties (30j)", "0", '#5cb85c')
        self.card_sort.pack(side='left', padx=10, expand=True, fill='x')
        self.card_fuel = StatCard(cards, "Carburant (30j)", "0 €", '#f0ad4e')
        self.card_fuel.pack(side='left', padx=10, expand=True, fill='x')
        self.card_maint = StatCard(cards, "Maintenance (30j)", "0 €", '#d9534f')
        self.card_maint.pack(side='left', padx=10, expand=True, fill='x')
        if HAS_MATPLOTLIB:
            gf = tk.Frame(f1, bg='white')
            gf.pack(fill='both', expand=True, padx=10, pady=10)
            self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4))
            self.fig.patch.set_facecolor('white')
            self.canvas = FigureCanvasTkAgg(self.fig, gf)
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Costs
        f2 = tk.Frame(self.notebook, bg='white')
        self.notebook.add(f2, text='Coûts')
        cols = [('veh', 'Véhicule', 180), ('carb', 'Carburant', 120), ('maint', 'Maintenance', 120), ('total', 'Total', 120)]
        self.tree_costs = FilterableTreeview(f2, columns=cols)
        self.tree_costs.pack(fill='both', expand=True, padx=10, pady=10)
        self.total_frame = tk.Frame(f2, bg='#f5f5f5', pady=10)
        self.total_frame.pack(fill='x', padx=10)
        self.label_total = tk.Label(self.total_frame, text="Total: 0 €", font=('Helvetica', 12, 'bold'), bg='#f5f5f5', fg='#000000')
        self.label_total.pack()

        # Usage
        f3 = tk.Frame(self.notebook, bg='white')
        self.notebook.add(f3, text='Utilisation')
        cols2 = [('veh', 'Véhicule', 180), ('km', 'Km', 120), ('sort', 'Sorties', 100), ('jours', 'Jours', 100), ('taux', 'Taux', 100)]
        self.tree_usage = FilterableTreeview(f3, columns=cols2)
        self.tree_usage.pack(fill='both', expand=True, padx=10, pady=10)

        # Top
        f4 = tk.Frame(self.notebook, bg='white')
        self.notebook.add(f4, text='Top')
        cols3 = [('rang', '#', 60), ('emp', 'Employé', 200), ('sort', 'Sorties', 100), ('km', 'Km', 120)]
        self.tree_top = FilterableTreeview(f4, columns=cols3)
        self.tree_top.pack(fill='both', expand=True, padx=10, pady=10)
    
    def refresh(self):
        stats = self.controller.get_overview()
        self.card_veh.set_value(str(stats['total_vehicles']))
        self.card_sort.set_value(str(stats['sorties_30j']))
        self.card_fuel.set_value(f"{stats['cout_carburant_30j']:.0f} €")
        self.card_maint.set_value(f"{stats['cout_maintenance_30j']:.0f} €")
        
        if HAS_MATPLOTLIB:
            self.ax1.clear()
            labels = ['Dispo', 'Sortie', 'Maint', 'Panne']
            sizes = [stats['disponibles'], stats['en_sortie'], stats['en_maintenance'], stats['en_panne']]
            clrs = ['#27ae60', '#f39c12', '#3498db', '#e74c3c']
            non_zero = [(l, s, c) for l, s, c in zip(labels, sizes, clrs) if s > 0]
            if non_zero:
                l, s, c = zip(*non_zero)
                self.ax1.pie(s, labels=l, colors=c, autopct='%1.0f%%')
            self.ax1.set_title('Répartition')
            
            self.ax2.clear()
            monthly = self.controller.get_monthly_costs(6)
            if monthly:
                mois = [m['mois'] for m in monthly]
                carb = [m['carburant'] for m in monthly]
                maint = [m['maintenance'] for m in monthly]
                x = range(len(mois))
                self.ax2.bar([i - 0.175 for i in x], carb, 0.35, label='Carburant', color='#f39c12')
                self.ax2.bar([i + 0.175 for i in x], maint, 0.35, label='Maintenance', color='#3498db')
                self.ax2.set_xticks(x)
                self.ax2.set_xticklabels(mois, rotation=45)
                self.ax2.legend()
            self.ax2.set_title('Coûts mensuels')
            self.fig.tight_layout()
            self.canvas.draw()
        
        self.tree_costs.clear()
        total = 0
        for c in self.controller.get_costs_by_vehicle():
            t = (c['carburant'] or 0) + (c['maintenance'] or 0)
            total += t
            self.tree_costs.insert(values=(f"{c['immatriculation']} ({c['marque']})", f"{c['carburant'] or 0:.2f} €",
                f"{c['maintenance'] or 0:.2f} €", f"{t:.2f} €"))
        self.label_total.config(text=f"Total: {total:.2f} €")
        
        self.tree_usage.clear()
        for u in self.controller.get_usage_by_vehicle():
            km = f"{u['km_actuel']:,}".replace(',', ' ') if u['km_actuel'] else '-'
            taux = f"{u['taux_utilisation']:.0f}%" if u.get('taux_utilisation') else '-'
            self.tree_usage.insert(values=(f"{u['immatriculation']} ({u['marque']})", km, u['sorties_30j'], u['jours_utilises'], taux))
        
        self.tree_top.clear()
        for i, e in enumerate(self.controller.get_top_employees(10), 1):
            km = f"{e['km_total']:,}".replace(',', ' ') if e['km_total'] else '0'
            self.tree_top.insert(values=(f"#{i}", f"{e['prenom']} {e['nom']}", e['nb_sorties'], km))
    
    def _export_csv(self):
        try:
            path = self.controller.export_csv(self.app.current_user.id)
            messagebox.showinfo("Export", f"CSV exporté:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def _export_pdf(self):
        try:
            path = self.controller.export_pdf(self.app.current_user.id)
            messagebox.showinfo("Export", f"PDF exporté:\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
