import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Main import get_access_token, get_all_flights
from tkcalendar import DateEntry

def run_search():
    ret_trip = ret_var.get()
    flex = flex_var.get()

    # Prefer DateEntry.get_date() which returns a date object
    try:
        dep_date_obj = dep_entry.get_date()
        dep_date = dep_date_obj.isoformat()
    except Exception:
        # Fallback: try to parse text entry
        dep_date = dep_entry.get()
        try:
            datetime.strptime(dep_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid departure date format. Use YYYY-MM-DD.")
            return

    # Return date handling
    ret_date = None
    if ret_trip:
        try:
            ret_date_obj = ret_entry.get_date()
            ret_date = ret_date_obj.isoformat()
        except Exception:
            ret_date = ret_entry.get()
            try:
                datetime.strptime(ret_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Invalid return date format. Use YYYY-MM-DD.")
                return

    token = get_access_token()
    if not token:
        messagebox.showerror("Auth Error", "Could not retrieve access token.")
        return

    # Patch get_all_flights to accept params directly (for GUI use)
    flights, _ = get_all_flights(token, dep_date, ret_trip, flex, ret_date)
    if not flights:
        messagebox.showinfo("No Results", "No flights found for your search.")
        return
    # Show results in a new window
    result_win = tk.Toplevel(root)
    result_win.title("Flight Results")
    text = tk.Text(result_win, wrap=tk.WORD, width=100, height=30)
    text.pack(expand=True, fill=tk.BOTH)
    for flight in flights:
        if 'searched_departure_date' in flight or 'searched_return_date' in flight:
            dep = flight.get('searched_departure_date', 'N/A')
            ret = flight.get('searched_return_date', 'N/A')
            text.insert(tk.END, f"Departure: {dep}  Return: {ret}\n")
        else:
            text.insert(tk.END, f"Date: {flight.get('searched_date')}\n")
        itineraries = flight.get('itineraries', [])
        if itineraries:
            text.insert(tk.END, "  Outbound Flight:\n")
            for seg in itineraries[0].get('segments', []):
                d = seg['departure']
                a = seg['arrival']
                text.insert(tk.END, f"    {d['iataCode']} ({d.get('at')}) -> {a['iataCode']} ({a.get('at')})\n")
            if len(itineraries) > 1:
                text.insert(tk.END, "  Return Flight:\n")
                for seg in itineraries[1].get('segments', []):
                    d = seg['departure']
                    a = seg['arrival']
                    text.insert(tk.END, f"    {d['iataCode']} ({d.get('at')}) -> {a['iataCode']} ({a.get('at')})\n")
        # Print the price for this specific offer (safe access)
        price = flight.get('price', {}).get('grandTotal')
        currency = flight.get('price', {}).get('currency')
        if price is None:
            price_str = "N/A"
        else:
            try:
                price_str = f"{float(price):.2f}"
            except Exception:
                price_str = str(price)
        text.insert(tk.END, f"  Total Price: {price_str} {currency if currency else ''}\n")
        text.insert(tk.END, "-"*50 + "\n")

root = tk.Tk()
root.title("Flight Finder GUI")

mainframe = ttk.Frame(root, padding="10 10 10 10")
mainframe.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Departure date
ttk.Label(mainframe, text="Departure Date (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W)
dep_entry = DateEntry(mainframe, width=15)
dep_entry.grid(row=0, column=1, sticky=tk.W)

# Return trip
ret_var = tk.BooleanVar()
ret_check = ttk.Checkbutton(mainframe, text="Return Trip", variable=ret_var)
ret_check.grid(row=1, column=0, sticky=tk.W)

# Return date
ttk.Label(mainframe, text="Return Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W)
ret_entry = DateEntry(mainframe, width=15)
ret_entry.grid(row=2, column=1, sticky=tk.W)

# Flexible search
flex_var = tk.BooleanVar()
flex_check = ttk.Checkbutton(mainframe, text="Flexible (±3 days, cheapest)", variable=flex_var)
flex_check.grid(row=3, column=0, sticky=tk.W)

# Search button
search_btn = ttk.Button(mainframe, text="Search Flights", command=run_search)
search_btn.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
