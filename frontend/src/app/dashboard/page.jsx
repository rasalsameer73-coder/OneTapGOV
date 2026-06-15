'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '../../lib/supabaseClient'
import ChatAssistant from './ChatAssistant'

export default function Dashboard() {
  const [name, setName] = useState('')
  const router = useRouter()

  useEffect(() => {
    const getProfile = async () => {
      const {
        data: {user},
      } = await supabase.auth.getUser()

      if (!user) {
        router.push('/login')
        return
      }

      const { data } = await supabase
      .from('profiles')
      .select('full_name')
      .eq('id', user.id)
      .single()

      if (data) {
        setName(data.full_name)
      }
    }

    getProfile()
  }, [router])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }
  
  return(
    <div className="min-h-screen bg-gray-100">

      <span className="text-gray-700 font-medium">Welcome, {name || 'User'}</span>
      <button onClick={handleLogout} className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">
        Logout</button>

      <div className="lg:col-span-2">
        <ChatAssistant />
      </div>
    </div>
  )
}