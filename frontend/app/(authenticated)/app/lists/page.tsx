'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useGANGUStore, type SavedList } from '@/lib/store'
import { ListOrdered, Plus, Send, Trash2, Sparkles, X } from 'lucide-react'

export default function ListsPage() {
  const router = useRouter()
  const { savedLists, addSavedList, removeSavedList } = useGANGUStore()

  const [creating, setCreating] = useState(false)
  const [draftName, setDraftName] = useState('')
  const [draftItem, setDraftItem] = useState('')
  const [draftItems, setDraftItems] = useState<string[]>([])

  const handleCreate = () => {
    if (!draftName.trim() || draftItems.length === 0) return
    const list: SavedList = {
      id: `list-${Date.now()}`,
      name: draftName.trim(),
      items: draftItems,
    }
    addSavedList(list)
    setCreating(false)
    setDraftName('')
    setDraftItems([])
    setDraftItem('')
  }

  const handleDispatch = (list: SavedList) => {
    const message = `Order ${list.items.join(', ')}`
    sessionStorage.setItem('gangu-prefill', message)
    router.push('/app')
  }

  return (
    <main className="min-h-screen pb-12">
      <div className="max-w-5xl mx-auto px-5 md:px-8 pt-8 md:pt-10">
        <header className="mb-8 flex items-end justify-between gap-4">
          <div>
            <span className="pill-violet mb-3 inline-flex">
              <ListOrdered className="w-3 h-3" />
              Saved lists
            </span>
            <h1 className="text-display text-3xl md:text-4xl mb-2">Your shopping lists</h1>
            <p className="text-slate-400">Save the things you reorder regularly. Tap once to send the whole list.</p>
          </div>
          <button onClick={() => setCreating(true)} className="btn-primary text-sm flex-shrink-0">
            <Plus className="w-4 h-4" />
            New list
          </button>
        </header>

        {creating && (
          <div className="surface-card p-6 mb-5 animate-rise">
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-display text-xl">Create a list</h3>
              <button
                onClick={() => {
                  setCreating(false)
                  setDraftName('')
                  setDraftItems([])
                }}
                className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 flex items-center justify-center text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <input
              type="text"
              value={draftName}
              onChange={(e) => setDraftName(e.target.value)}
              placeholder="List name (e.g. Weekly basics)"
              className="input-base mb-3"
            />

            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={draftItem}
                onChange={(e) => setDraftItem(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && draftItem.trim()) {
                    setDraftItems((arr) => [...arr, draftItem.trim()])
                    setDraftItem('')
                  }
                }}
                placeholder="Add item, e.g. Atta 5 kg"
                className="input-base flex-1"
              />
              <button
                onClick={() => {
                  if (draftItem.trim()) {
                    setDraftItems((arr) => [...arr, draftItem.trim()])
                    setDraftItem('')
                  }
                }}
                className="btn-secondary"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>

            {draftItems.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-5">
                {draftItems.map((it, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-200 text-sm font-semibold"
                  >
                    {it}
                    <button
                      onClick={() => setDraftItems((arr) => arr.filter((_, j) => j !== i))}
                      className="text-amber-300/60 hover:text-amber-200"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            <button
              onClick={handleCreate}
              disabled={!draftName.trim() || draftItems.length === 0}
              className="btn-primary w-full"
            >
              <Sparkles className="w-4 h-4" />
              Save list
            </button>
          </div>
        )}

        {savedLists.length === 0 && !creating ? (
          <div className="surface-card p-10 text-center">
            <ListOrdered className="w-10 h-10 mx-auto mb-4 text-slate-700" />
            <p className="text-slate-400 mb-5">No saved lists yet.</p>
            <button onClick={() => setCreating(true)} className="btn-primary">
              <Plus className="w-4 h-4" />
              Create your first list
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {savedLists.map((list) => (
              <article key={list.id} className="surface-card p-6">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div>
                    <h3 className="text-display text-xl mb-1">{list.name}</h3>
                    <p className="text-xs text-slate-500">
                      {list.items.length} items
                      {list.lastUsed && (
                        <>
                          <span className="text-slate-700 mx-2">·</span>
                          last used {list.lastUsed}
                        </>
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => removeSavedList(list.id)}
                    className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 hover:bg-rose-500/15 hover:border-rose-500/30 hover:text-rose-300 text-slate-500 flex items-center justify-center transition-all"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <ul className="space-y-1.5 mb-5">
                  {list.items.map((item, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                      <span className="w-1 h-1 rounded-full bg-amber-400" />
                      {item}
                    </li>
                  ))}
                </ul>

                <button onClick={() => handleDispatch(list)} className="btn-primary w-full text-sm">
                  <Send className="w-4 h-4" />
                  Order whole list
                </button>
              </article>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
