import { useState, useCallback } from 'react'

/**
 * Custom hook for managing modal states
 * Replaces the ModalHelper from vanilla JS
 */
export function useModal() {
  // Confirm modal state
  const [confirmModal, setConfirmModal] = useState({
    open: false,
    title: 'Potwierdzenie',
    message: '',
    resolve: null
  })

  // Alert modal state
  const [alertModal, setAlertModal] = useState({
    open: false,
    title: 'Informacja',
    message: '',
    resolve: null
  })

  // Error modal state
  const [errorModal, setErrorModal] = useState({
    open: false,
    title: 'Błąd',
    message: '',
    resolve: null
  })

  /**
   * Show confirmation dialog
   * Returns a promise that resolves to true/false
   */
  const showConfirm = useCallback((message, title = 'Potwierdzenie') => {
    return new Promise((resolve) => {
      setConfirmModal({
        open: true,
        title,
        message,
        resolve
      })
    })
  }, [])

  /**
   * Handle confirm modal response
   */
  const handleConfirm = useCallback((confirmed) => {
    if (confirmModal.resolve) {
      confirmModal.resolve(confirmed)
    }
    setConfirmModal({ open: false, title: '', message: '', resolve: null })
  }, [confirmModal])

  /**
   * Show alert dialog
   * Returns a promise that resolves when closed
   */
  const showAlert = useCallback((message, title = 'Informacja') => {
    return new Promise((resolve) => {
      setAlertModal({
        open: true,
        title,
        message,
        resolve
      })
    })
  }, [])

  /**
   * Handle alert modal close
   */
  const handleAlertClose = useCallback(() => {
    if (alertModal.resolve) {
      alertModal.resolve()
    }
    setAlertModal({ open: false, title: '', message: '', resolve: null })
  }, [alertModal])

  /**
   * Show error dialog
   * Returns a promise that resolves when closed
   */
  const showError = useCallback((message, title = 'Błąd') => {
    return new Promise((resolve) => {
      setErrorModal({
        open: true,
        title,
        message,
        resolve
      })
    })
  }, [])

  /**
   * Handle error modal close
   */
  const handleErrorClose = useCallback(() => {
    if (errorModal.resolve) {
      errorModal.resolve()
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
