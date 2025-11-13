
// ============================================
// components/SessionRestoreDialog.tsx
// ============================================
import { FC } from 'react'
import { 
  Dialog, 
  Classes, 
  Button,
  Callout,
  Intent,
} from '@blueprintjs/core'

interface SessionRestoreDialogProps {
  isOpen: boolean
  sessionInfo: { timestamp: string; holesCount: number } | null
  onRestore: () => void
  onDismiss: () => void
}

export const SessionRestoreDialog: FC<SessionRestoreDialogProps> = ({
  isOpen,
  sessionInfo,
  onRestore,
  onDismiss,
}) => {
  if (!sessionInfo) return null

  const date = new Date(sessionInfo.timestamp)
  const timeAgo = getTimeAgo(date)

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onDismiss}
      title="Restore Previous Session"
      icon="history"
      className={Classes.DARK}
      style={{ width: '500px' }}
    >
      <div className={Classes.DIALOG_BODY}>
        <Callout intent="primary" icon="info-sign">
          <p style={{ margin: 0 }}>
            A previous session was found from <strong>{timeAgo}</strong>
          </p>
          <p style={{ marginTop: '8px', marginBottom: 0 }}>
            <strong>{sessionInfo.holesCount}</strong> drillholes were loaded.
          </p>
        </Callout>

        <p style={{ marginTop: '16px', color: '#8A9BA8' }}>
          Would you like to restore this session or start fresh?
        </p>
      </div>

      <div className={Classes.DIALOG_FOOTER}>
        <div className={Classes.DIALOG_FOOTER_ACTIONS}>
          <Button onClick={onDismiss}>
            Start Fresh
          </Button>
          <Button 
            intent="primary"
            onClick={onRestore}
            icon="history"
          >
            Restore Session
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

function getTimeAgo(date: Date): string {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  
  return date.toLocaleDateString()
}