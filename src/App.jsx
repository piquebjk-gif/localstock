import { useState } from 'react'
import './App.css'

const INITIAL_ITEMS = [
  { id: 1, name: 'Ürün A', quantity: 50, unit: 'adet', minStock: 10 },
  { id: 2, name: 'Ürün B', quantity: 8, unit: 'kg', minStock: 15 },
  { id: 3, name: 'Ürün C', quantity: 120, unit: 'litre', minStock: 20 },
]

export default function App() {
  const [items, setItems] = useState(INITIAL_ITEMS)
  const [form, setForm] = useState({ name: '', quantity: '', unit: 'adet', minStock: '' })
  const [search, setSearch] = useState('')

  const filtered = items.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase())
  )

  function addItem(e) {
    e.preventDefault()
    if (!form.name.trim() || !form.quantity) return
    setItems(prev => [
      ...prev,
      {
        id: Date.now(),
        name: form.name.trim(),
        quantity: Number(form.quantity),
        unit: form.unit,
        minStock: Number(form.minStock) || 0,
      },
    ])
    setForm({ name: '', quantity: '', unit: 'adet', minStock: '' })
  }

  function deleteItem(id) {
    setItems(prev => prev.filter(i => i.id !== id))
  }

  function updateQuantity(id, delta) {
    setItems(prev =>
      prev.map(i => i.id === id ? { ...i, quantity: Math.max(0, i.quantity + delta) } : i)
    )
  }

  const lowStock = items.filter(i => i.quantity <= i.minStock)

  return (
    <div className="app">
      <header className="header">
        <h1>LocalStock</h1>
        <span className="subtitle">Offline Stok Yönetimi</span>
      </header>

      {lowStock.length > 0 && (
        <div className="alert">
          Kritik stok uyarisi: {lowStock.map(i => i.name).join(', ')}
        </div>
      )}

      <div className="container">
        <section className="card">
          <h2>Yeni Urun Ekle</h2>
          <form onSubmit={addItem} className="form">
            <input
              placeholder="Urun adi"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              required
            />
            <input
              type="number"
              placeholder="Miktar"
              value={form.quantity}
              onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))}
              min="0"
              required
            />
            <select value={form.unit} onChange={e => setForm(f => ({ ...f, unit: e.target.value }))}>
              <option>adet</option>
              <option>kg</option>
              <option>litre</option>
              <option>kutu</option>
            </select>
            <input
              type="number"
              placeholder="Min. stok"
              value={form.minStock}
              onChange={e => setForm(f => ({ ...f, minStock: e.target.value }))}
              min="0"
            />
            <button type="submit" className="btn-primary">Ekle</button>
          </form>
        </section>

        <section className="card">
          <div className="list-header">
            <h2>Stok Listesi ({items.length})</h2>
            <input
              className="search"
              placeholder="Ara..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
          <table className="table">
            <thead>
              <tr>
                <th>Urun</th>
                <th>Miktar</th>
                <th>Birim</th>
                <th>Durum</th>
                <th>Islemler</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => (
                <tr key={item.id} className={item.quantity <= item.minStock ? 'row-low' : ''}>
                  <td>{item.name}</td>
                  <td className="qty-cell">
                    <button onClick={() => updateQuantity(item.id, -1)} className="btn-sm">-</button>
                    <strong>{item.quantity}</strong>
                    <button onClick={() => updateQuantity(item.id, 1)} className="btn-sm">+</button>
                  </td>
                  <td>{item.unit}</td>
                  <td>
                    <span className={`badge ${item.quantity <= item.minStock ? 'badge-low' : 'badge-ok'}`}>
                      {item.quantity <= item.minStock ? 'Kritik' : 'Normal'}
                    </span>
                  </td>
                  <td>
                    <button onClick={() => deleteItem(item.id)} className="btn-danger">Sil</button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={5} className="empty">Urun bulunamadi</td></tr>
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  )
}
