'use client'

import { useGANGUStore } from '@/lib/store'
import { Check, Loader, AlertCircle, X } from 'lucide-react'
import { cancelProcessing } from '@/lib/api'
import { useState } from 'react'

const STEP_LABELS: Record<string, string> = {
  'init': '🎯 Initializing',
  'intent_extraction': '🧠 Understanding Request',
  'task_planning': '📋 Planning Tasks',
  'search': '🔍 Searching Platforms',
  'comparison': '⚖️ Comparing Products',
  'decision': '✨ Selecting Best Option',
  'purchase': '🛒 Processing Order',
  'notification': '📧 Sending Notification',
  'error': '⚠️ Error Occurred'
}

const STEP_ORDER = [
  'intent_extraction',
  'task_planning',
  'search',
  'comparison',
  'decision',
  'purchase',
  'notification'
]

export default function AgentTimeline() {
  const { agentSteps, currentStep, sessionId, isCancelling, setCancelling, setCancelled, setProcessing } = useGANGUStore()
  const [cancelError, setCancelError] = useState('')
  
  // Handle cancel
  const handleCancel = async () => {
    if (!sessionId) return
    
    try {
      // Immediately show cancelling state
      setCancelling(true)
      setProcessing(false)
      setCancelError('')
      
      // Show cancelled status immediately in UI
      console.log('⏹️ CANCELLING ORDER IMMEDIATELY...')
      
      // Send cancel request to backend
      await cancelProcessing(sessionId)
      
      // Mark as fully cancelled
      setCancelled(true)
      console.log('✅ Order cancelled successfully')
      
      // Show success message
      setTimeout(() => {
        alert('✅ Order cancelled successfully!')
      }, 300)
      
    } catch (error) {
      console.error('Cancel error:', error)
      setCancelError('Failed to cancel. Please try again.')
      setCancelling(false)
      setProcessing(true)  // Restore processing state if cancel failed
    }
  }

  // Show empty state when no steps
  if (agentSteps.length === 0) {
    return (
      <div className="gangu-card animate-fade-in">
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
            <span className="text-3xl">🤖</span>
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Agent Workflow</h3>
          <p className="text-slate-400 text-sm">Agents will appear here once you make a request</p>
        </div>
      </div>
    )
  }

  // Check if all steps are complete
  const allComplete = agentSteps.length > 0 && agentSteps.every(step => step.status === 'complete')
  const hasError = agentSteps.some(step => step.status === 'error')
  
  // Count completed steps
  const completedCount = agentSteps.filter(step => step.status === 'complete').length
  const totalSteps = STEP_ORDER.length

  // Create a map of step statuses
  const stepStatusMap: Record<string, 'processing' | 'complete' | 'pending'> = {}
  agentSteps.forEach(step => {
    stepStatusMap[step.step] = step.status as 'processing' | 'complete'
  })

  return (
    <div className="gangu-card animate-fade-in">
      {/* Header with Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl font-bold gradient-text">
            {allComplete ? '✅ All Agents Done!' : hasError ? '⚠️ Issue Occurred' : isCancelling ? '⏹️ Cancelling...' : '🤖 Agents Working...'}
          </h3>
          <div className="flex items-center space-x-2">
            {!allComplete && !hasError && !isCancelling && (
              <>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
                <span className="text-xs text-slate-400 font-medium">Live</span>
              </>
            )}
            {allComplete && (
              <span className="text-xs text-green-400 font-medium flex items-center">
                <Check className="w-3 h-3 mr-1" /> Complete
              </span>
            )}
          </div>
        </div>
        
        {/* Cancel Button - Show only when processing and not cancelled */}
        {!allComplete && !hasError && !isCancelling && (
          <button
            onClick={handleCancel}
            className="w-full mb-3 px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 active:bg-red-500/30 border border-red-500/30 hover:border-red-500/50 rounded-lg text-red-400 text-sm font-semibold flex items-center justify-center space-x-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <X className="w-5 h-5 animate-pulse" />
            <span>⚠️ CANCEL ORDER NOW</span>
          </button>
        )}
        
        {/* Cancelling Status */}
        {isCancelling && (
          <div className="w-full mb-3 px-4 py-2.5 bg-red-500/20 border-2 border-red-500/50 rounded-lg text-red-300 text-sm font-bold flex items-center justify-center space-x-2">
            <X className="w-5 h-5 animate-spin" />
            <span>⏹️ CANCELLING...</span>
          </div>
        )}
        
        {/* Cancel Error */}
        {cancelError && (
          <div className="mb-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
            {cancelError}
          </div>
        )}
        
        {/* Progress Bar */}
        <div className="mb-2">
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
              style={{ width: `${(completedCount / totalSteps) * 100}%` }}
            />
          </div>
        </div>
        
        {/* Progress Text */}
        <div className="flex justify-between items-center text-xs">
          <span className="text-slate-400">
            {completedCount} of {totalSteps} agents completed
          </span>
          <span className="text-blue-400 font-semibold">
            {Math.round((completedCount / totalSteps) * 100)}%
          </span>
        </div>
      </div>

      {/* Sequential Timeline View */}
      <div className="relative">
        {/* Vertical connecting line */}
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-slate-700"></div>

        <div className="space-y-4">
          {STEP_ORDER.map((stepKey, index) => {
            const stepData = agentSteps.find(s => s.step === stepKey)
            const status = stepStatusMap[stepKey] || 'pending'
            const isActive = stepData?.status === 'processing'
            const isComplete = stepData?.status === 'complete'
            const isPending = !stepData || status === 'pending'

            return (
              <div
                key={stepKey}
                className="relative flex items-start space-x-3 transition-all duration-300"
              >
                {/* Step indicator */}
                <div className="relative z-10 flex-shrink-0">
                  {isComplete && (
                    <div className="w-10 h-10 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center">
                      <Check className="w-5 h-5 text-green-400" />
                    </div>
                  )}
                  {isActive && (
                    <div className="w-10 h-10 rounded-full bg-blue-500/20 border-2 border-blue-500 flex items-center justify-center">
                      <Loader className="w-5 h-5 text-blue-400 animate-spin" />
                    </div>
                  )}
                  {isPending && (
                    <div className="w-10 h-10 rounded-full bg-slate-700/50 border-2 border-slate-600 flex items-center justify-center">
                      <div className="w-2.5 h-2.5 rounded-full bg-slate-500"></div>
                    </div>
                  )}
                </div>

                {/* Step content */}
                <div className="flex-grow pb-1">
                  <div className={`p-3 rounded-lg border transition-all ${
                    isComplete ? 'bg-green-500/5 border-green-500/30' :
                    isActive ? 'bg-blue-500/10 border-blue-500/40' :
                    'bg-slate-800/50 border-slate-700/50'
                  }`}>
                    <h4 className={`font-bold text-base mb-0.5 ${
                      isComplete ? 'text-green-400' :
                      isActive ? 'text-blue-400' :
                      'text-slate-400'
                    }`}>
                      {STEP_LABELS[stepKey]}
                    </h4>
                    
                    {stepData && stepData.message && (
                      <>
                        <p className={`text-xs ${
                          isComplete || isActive ? 'text-slate-300' : 'text-slate-500'
                        }`}>
                          {stepData.message}
                        </p>
                        
                        {/* Show platform badges for search step */}
                        {stepKey === 'search' && isComplete && stepData.data?.platforms && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {stepData.data.platforms.map((platform: string, i: number) => (
                              <span
                                key={i}
                                className="px-2 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-xs font-semibold text-blue-300"
                              >
                                {platform === 'Amazon' ? '📦' : '⚡'} {platform}
                              </span>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                    
                    {isPending && (
                      <p className="text-xs text-slate-500">Waiting...</p>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
