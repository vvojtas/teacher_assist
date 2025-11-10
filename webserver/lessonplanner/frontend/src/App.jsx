import { useState } from 'react'
import { ThemeInput } from './components/ThemeInput'
import { ActionBar } from './components/ActionBar'
import { ProgressBar } from './components/ProgressBar'
import { PlanTable } from './components/PlanTable'
import { ConfirmDialog } from './components/Modals/ConfirmDialog'
import { InfoDialog } from './components/Modals/InfoDialog'
import { ErrorDialog } from './components/Modals/ErrorDialog'
import { useTableManager } from './hooks/useTableManager'
import { useAIService } from './hooks/useAIService'
import { useClipboard } from './hooks/useClipboard'
import { useModal } from './hooks/useModal'

function App() {
  const [theme, setTheme] = useState('')
  const [selectedRows, setSelectedRows] = useState(new Set())
  const [bulkGenerating, setBulkGenerating] = useState(false)
  const [progress, setProgress] = useState({ visible: false, value: 0, text: '' })

  const {
    rows,
    addRows,
    deleteRow,
    clearAll,
    updateRow,
    setRowLoading,
    getRowsNeedingGeneration,
    markUserEdited
  } = useTableManager()

  const { generateSingle, generateBulk } = useAIService()
  const { copyToClipboard } = useClipboard()
  const {
    confirmModal,
    showConfirm,
    handleConfirm,
    alertModal,
    showAlert,
    handleAlertClose,
    errorModal,
    showError,
    handleErrorClose
  } = useModal()

  // Handle single row generation
  const handleGenerate = async (rowId) => {
    const row = rows.find(r => r.id === rowId)
    if (!row) return

    if (!row.activity.trim()) {
      await showAlert('Pole "Aktywność" nie może być puste.')
      return
    }

    // Check if user has already filled in metadata fields
    const hasManualData = row.module || row.curriculum || row.objectives
    if (hasManualData) {
      const confirmed = await showConfirm('Wiersz zawiera dane wprowadzone ręcznie. Nadpisać dane AI?')
      if (!confirmed) return
    }

    try {
      setRowLoading(rowId, true)
      const data = await generateSingle(row.activity, theme)
      updateRow(rowId, data)
    } catch (error) {
      await showError(error.message)
    } finally {
      setRowLoading(rowId, false)
    }
  }

  // Handle regeneration
  const handleRegenerate = async (rowId) => {
    const row = rows.find(r => r.id === rowId)
    if (!row) return

    if (!row.activity.trim()) {
      await showAlert('Pole "Aktywność" nie może być puste.')
      return
    }

    // Check if user edited the row
    if (row.userEdited) {
      const confirmed = await showConfirm('Wiersz był zmodyfikowany. Nadpisać dane wprowadzone przez użytkownika?')
      if (!confirmed) return
    }

    try {
      setRowLoading(rowId, true)
      const data = await generateSingle(row.activity, theme)
      updateRow(rowId, data)
    } catch (error) {
      await showError(error.message)
    } finally {
      setRowLoading(rowId, false)
    }
  }

  // Handle bulk generation
  const handleBulkGenerate = async () => {
    const rowsToProcess = getRowsNeedingGeneration()

    if (rowsToProcess.length === 0) {
      await showAlert('Brak nowych aktywności do przetworzenia. Wszystkie wiersze są już wypełnione lub puste.')
      return
    }

    setBulkGenerating(true)
    setProgress({ visible: true, value: 0, text: `Przetwarzanie... (0/${rowsToProcess.length})` })

    // Set all rows to loading state
    rowsToProcess.forEach(row => setRowLoading(row.id, true))

    try {
      const results = await generateBulk(rowsToProcess, theme, (result) => {
        const progressPercent = (result.completed / result.total) * 100
        setProgress({
          visible: true,
          value: progressPercent,
          text: `Przetwarzanie... (${result.completed}/${result.total})`
        })

        if (result.success) {
          updateRow(result.rowId, result.data)
        }

        setRowLoading(result.rowId, false)
      })

      // Show completion message
      if (results.failed.length > 0) {
        const failureDetails = results.failed.map(f =>
          `• ${f.activity.substring(0, 40)}...\n  Błąd: ${f.error}`
        ).join('\n\n')

        setProgress({
          visible: true,
          value: 100,
          text: `Ukończono: ${results.succeeded}/${results.total}. Nieudane: ${results.failed.length}`
        })

        await showError(
          `Przetworzono pomyślnie: ${results.succeeded}/${results.total}\n\n` +
          `Nieudane wiersze (${results.failed.length}):\n\n${failureDetails}`
        )
      } else {
        setProgress({
          visible: true,
          value: 100,
          text: `Ukończono: ${results.succeeded}/${results.total}`
        })
      }

      // Hide progress after delay
      setTimeout(() => {
        setProgress({ visible: false, value: 0, text: '' })
      }, 2000)

    } catch (error) {
      await showError(error.message)
    } finally {
      setBulkGenerating(false)
      rowsToProcess.forEach(row => setRowLoading(row.id, false))
    }
  }

  // Handle row deletion
  const handleDelete = (rowId) => {
    deleteRow(rowId)
    // Remove from selected rows if it was selected
    setSelectedRows(prev => {
      const next = new Set(prev)
      next.delete(rowId)
      return next
    })
  }

  // Handle clear all
  const handleClearAll = async () => {
    const confirmed = await showConfirm('Czy na pewno chcesz wyczyść wszystkie wiersze?')
    if (confirmed) {
      clearAll()
      setTheme('')
      setSelectedRows(new Set())
    }
  }

  // Handle row selection
  const handleSelectChange = (rowId, checked) => {
    setSelectedRows(prev => {
      const next = new Set(prev)
      if (checked) {
        next.add(rowId)
      } else {
        next.delete(rowId)
      }
      return next
    })
  }

  // Handle copy to clipboard
  const handleCopyTable = async () => {
    try {
      let rowsToCopy
      let includeHeaders

      if (selectedRows.size > 0) {
        // Copy only selected rows
        rowsToCopy = rows.filter(row => selectedRows.has(row.id))
        includeHeaders = false
      } else {
        // Copy all rows
        rowsToCopy = rows
        includeHeaders = true
      }

      if (rowsToCopy.length === 0) {
        await showAlert('Brak wierszy do skopiowania.')
        return
      }

      await copyToClipboard(rowsToCopy, includeHeaders)

      const message = selectedRows.size > 0
        ? `Skopiowano ${rowsToCopy.length} zaznaczonych wierszy do schowka.`
        : `Skopiowano całą tabelę (${rowsToCopy.length} wierszy) do schowka.`

      await showAlert(message)

      // Uncheck all checkboxes after successful copy
      if (selectedRows.size > 0) {
        setSelectedRows(new Set())
      }
    } catch (error) {
      await showError(error.message)
    }
  }

  return (
    <div className="container mx-auto py-6 px-4 max-w-7xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Teacher Assist - Planowanie Lekcji</h1>
      </div>

      {/* Theme Input */}
      <ThemeInput value={theme} onChange={setTheme} />

      {/* Action Bar */}
      <ActionBar
        bulkGenerating={bulkGenerating}
        selectedRowCount={selectedRows.size}
        onBulkGenerate={handleBulkGenerate}
        onAddRow={() => addRows(1)}
        onClearAll={handleClearAll}
        onCopyTable={handleCopyTable}
      />

      {/* Progress Bar */}
      <ProgressBar
        visible={progress.visible}
        progress={progress.value}
        text={progress.text}
      />

      {/* Plan Table */}
      <PlanTable
        rows={rows}
        selectedRows={selectedRows}
        onRowUpdate={updateRow}
        onGenerate={handleGenerate}
        onRegenerate={handleRegenerate}
        onDelete={handleDelete}
        onSelectChange={handleSelectChange}
        onMarkUserEdited={markUserEdited}
      />

      {/* Modals */}
      <ConfirmDialog
        open={confirmModal.open}
        title={confirmModal.title}
        message={confirmModal.message}
        onConfirm={() => handleConfirm(true)}
        onCancel={() => handleConfirm(false)}
      />

      <InfoDialog
        open={alertModal.open}
        title={alertModal.title}
        message={alertModal.message}
        onClose={handleAlertClose}
      />

      <ErrorDialog
        open={errorModal.open}
        title={errorModal.title}
        message={errorModal.message}
        onClose={handleErrorClose}
      />
    </div>
  )
}

export default App
