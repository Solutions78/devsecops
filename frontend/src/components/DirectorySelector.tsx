import { useState, useRef } from 'react'
import { Box, Button, TextField, InputAdornment } from '@mui/material'
import { FolderOpen as FolderIcon } from '@mui/icons-material'

interface DirectorySelectorProps {
  value: string
  onChange: (path: string) => void
  label?: string
  placeholder?: string
  disabled?: boolean
  required?: boolean
  buttonOnly?: boolean
}

export default function DirectorySelector({
  value,
  onChange,
  label = "Directory Path",
  placeholder = "~/path/to/directory",
  disabled = false,
  required = false,
  buttonOnly = false
}: DirectorySelectorProps) {
  // useRef hook to get reference to the hidden input element
  const hiddenInputRef = useRef<HTMLInputElement>(null)

  /**
   * Handle the directory selection using modern File System Access API when available,
   * falling back to webkitdirectory for older browsers
   */
  const handleSelectDirectory = async () => {
    try {
      // Try to use the modern File System Access API first (Chrome/Edge)
      if ('showDirectoryPicker' in window) {
        const directoryHandle = await (window as any).showDirectoryPicker()
        const directoryName = directoryHandle.name
        
        // Prompt user for full path since we can't get absolute paths due to security
        const userPath = prompt(
          `Selected directory: "${directoryName}"\n\n` +
          `Please enter the full path in format ~/path/to/directory:\n` +
          `(e.g., ~/Documents/${directoryName}, ~/Desktop/${directoryName}, etc.)`,
          `~/${directoryName}`
        )
        
        if (userPath && userPath.trim()) {
          let formattedPath = userPath.trim()
          if (!formattedPath.startsWith('~/')) {
            if (formattedPath.startsWith('/')) {
              formattedPath = `~${formattedPath}`
            } else {
              formattedPath = `~/${formattedPath}`
            }
          }
          onChange(formattedPath)
        }
      } else {
        // Fallback to webkitdirectory for older browsers
        if (hiddenInputRef.current) {
          hiddenInputRef.current.click()
        }
      }
    } catch (error) {
      // User cancelled or API not supported, fall back to input
      if (hiddenInputRef.current) {
        hiddenInputRef.current.click()
      }
    }
  }

  /**
   * Handle directory selection using modern File System Access API when available,
   * with fallback to webkitdirectory for older browsers
   */
  const handleDirectoryChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    
    if (files && files.length > 0) {
      // Get the relative path from the first file (we only use this to extract directory name)
      const relativePath = files[0].webkitRelativePath
      
      // Extract the directory name by splitting the path and getting the first element
      // For example: "my-folder/file1.txt" -> "my-folder"
      const pathParts = relativePath.split('/')
      const directoryName = pathParts[0]
      
      // Prompt user to provide the full path since we can't get absolute paths
      const userPath = prompt(
        `Selected directory: "${directoryName}"\n\n` +
        `Please enter the full path in format ~/path/to/directory:\n` +
        `(e.g., ~/Documents/${directoryName}, ~/Desktop/${directoryName}, etc.)`,
        `~/${directoryName}`
      )
      
      if (userPath && userPath.trim()) {
        // Ensure the path starts with ~/
        let formattedPath = userPath.trim()
        if (!formattedPath.startsWith('~/')) {
          if (formattedPath.startsWith('/')) {
            formattedPath = `~${formattedPath}`
          } else {
            formattedPath = `~/${formattedPath}`
          }
        }
        onChange(formattedPath)
      }
    }
    
    // Reset the input value to allow selecting the same directory again
    event.target.value = ''
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {/* Hidden file input configured for directory selection only */}
      <input
        ref={hiddenInputRef}
        type="file"
        webkitdirectory=""
        multiple
        style={{ display: 'none' }}
        onChange={handleDirectoryChange}
        disabled={disabled}
      />
      
      {buttonOnly ? (
        /* Button-only mode for use below text input */
        <Button
          variant="outlined"
          size="medium"
          startIcon={<FolderIcon />}
          onClick={handleSelectDirectory}
          disabled={disabled}
          sx={{ 
            alignSelf: 'flex-start',
            minWidth: 'auto', 
            whiteSpace: 'nowrap',
            textTransform: 'none'
          }}
        >
          Browse...
        </Button>
      ) : (
        /* Combined input + button mode */
        <TextField
          fullWidth
          label={label}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          disabled={disabled}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<FolderIcon />}
                  onClick={handleSelectDirectory}
                  disabled={disabled}
                  sx={{ minWidth: 'auto', whiteSpace: 'nowrap' }}
                >
                  Select Directory
                </Button>
              </InputAdornment>
            ),
          }}
        />
      )}
    </Box>
  )
}