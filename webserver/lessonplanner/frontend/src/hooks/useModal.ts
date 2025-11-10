import { useState, useCallback } from 'react'

interface ModalState {
  open: boolean
  title: string
  message: string
  resolve: ((value: boolean | void) => void) | null
}

/**
 * Custom hook for managing modal states
 * Replaces the ModalHelper from vanilla JS
 */
export function useModal() {
  // Confirm modal state
  const [confirmModal, setConfirmModal] = useState<ModalState>({
    open: false,
    title: 'Potwierdzenie',
    message: '',
    resolve: null
  })

  // Alert modal state
  const [alertModal, setAlertModal] = useState<ModalState>({
    open: false,
    title: 'Informacja',
    message: '',
    resolve: null
  })

  // Error modal state
  const [errorModal, setErrorModal] = useState<ModalState>({
    open: false,
    title: 'Błąd',
    message: '',
    resolve: null
  })

  /**
   * Show confirmation dialog
   * Returns a promise that resolves to true/false
   */
  const showConfirm = useCallback((message: string, title = 'Potwierdzenie'): Promise<boolean> => {
    return new Promise((resolve) => {
      setConfirmModal({
        open: true,
        title,
        message,
        resolve: resolve as (value: boolean) => void
      })
    })
  }, [])

  /**
   * Handle confirm modal response
   */
  const handleConfirm = useCallback((confirmed: boolean) => {
    if (confirmModal.resolve) {
      (confirmModal.resolve as (value: boolean) => void)(confirmed)
    }
    setConfirmModal({ open: false, title: '', message: '', resolve: null })
  }, [confirmModal])

  /**
   * Show alert dialog
   * Returns a promise that resolves when closed
   */
  const showAlert = useCallback((message: string, title = 'Informacja'): Promise<void> => {
    return new Promise((resolve) => {
      setAlertModal({
        open: true,
        title,
        message,
        resolve: resolve as () => void
      })
    })
  }, [])

  /**
   * Handle alert modal close
   */
  const handleAlertClose = useCallback(() => {
    if (alertModal.resolve) {
      (alertModal.resolve as () => void)()
    }
    setAlertModal({ open: false, title: '', message: '', resolve: null })
  }, [alertModal])

  /**
   * Show error dialog
   * Returns a promise that resolves when closed
   */
  const showError = useCallback((message: string, title = 'Błąd'): Promise<void> => {
    return new Promise((resolve) => {
      setErrorModal({
        open: true,
        title,
        message,
        resolve: resolve as () => void
      })
    })
  }, [])

  /**
   * Handle error modal close
   */
  const handleErrorClose = useCallback(() => {
    if (errorModal.resolve) {
      (errorModal.resolve as () => void)()
    }
    setErrorModal({ open: false, title: '', message: '', resolve: null })
  }, [errorModal])

  return {
    // Confirm modal
    confirmModal,
    showConfirm,
    handleConfirm,

    // Alert modal
    alertModal,
    showAlert,
    handleAlertClose,

    // Error modal
    errorModal,
    showError,
    handleErrorClose
  }
}
