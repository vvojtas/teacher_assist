import { useCallback } from 'react'

/**
 * Custom hook for copying table data to clipboard
 * Supports both HTML and TSV formats for compatibility with Google Docs/Excel
 */
export function useClipboard() {
  /**
   * Escape HTML special characters
   */
  const escapeHtml = useCallback((text) => {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }, [])

  /**
   * Build HTML table from rows
   */
  const buildHtmlTable = useCallback((rows, includeHeaders = true) => {
    let html = '<table border="1" style="border-collapse: collapse;">'

    // Add headers if needed
    if (includeHeaders) {
      html += '<thead><tr>'
      html += '<th style="padding: 8px; border: 1px solid #000;">Moduł</th>'
      html += '<th style="padding: 8px; border: 1px solid #000;">Podstawa Programowa</th>'
      html += '<th style="padding: 8px; border: 1px solid #000;">Cele</th>'
      html += '<th style="padding: 8px; border: 1px solid #000;">Aktywność</th>'
      html += '</tr></thead>'
    }

    // Add data rows
    html += '<tbody>'
    rows.forEach(row => {
      html += '<tr>'
      html += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(row.module)}</td>`
      html += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(row.curriculum)}</td>`
      html += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top; white-space: pre-wrap;">${escapeHtml(row.objectives)}</td>`
      html += `<td style="padding: 8px; border: 1px solid #000; vertical-align: top;">${escapeHtml(row.activity)}</td>`
      html += '</tr>'
    })
    html += '</tbody></table>'

    return html
  }, [escapeHtml])

  /**
   * Build TSV (tab-separated values) from rows
   */
  const buildTsvTable = useCallback((rows, includeHeaders = true) => {
    let tsv = ''

    if (includeHeaders) {
      tsv = 'Moduł\tPodstawa Programowa\tCele\tAktywność\n'
    }

    rows.forEach(row => {
      tsv += `${row.module}\t${row.curriculum}\t${row.objectives}\t${row.activity}\n`
    })

    return tsv
  }, [])

  /**
   * Copy rows to clipboard in both HTML and TSV formats
   */
  const copyToClipboard = useCallback(async (rows, includeHeaders = true) => {
    if (!rows || rows.length === 0) {
      throw new Error('Brak wierszy do skopiowania.')
    }

    const htmlTable = buildHtmlTable(rows, includeHeaders)
    const tsvTable = buildTsvTable(rows, includeHeaders)

    try {
      const htmlBlob = new Blob([htmlTable], { type: 'text/html' })
      const textBlob = new Blob([tsvTable], { type: 'text/plain' })

      const clipboardItem = new ClipboardItem({
        'text/html': htmlBlob,
        'text/plain': textBlob
      })

      await navigator.clipboard.write([clipboardItem])
      return true
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
      throw new Error('Nie udało się skopiować do schowka. Spróbuj ponownie.')
    }
  }, [buildHtmlTable, buildTsvTable])

  return {
    copyToClipboard
  }
}
