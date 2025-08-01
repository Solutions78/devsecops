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
}

export default function DirectorySelector({
  value,
  onChange,
  label = "Directory Path",
  placeholder = "~/path/to/directory",
  disabled = false,
  required = false
}: DirectorySelectorProps) {
  // useRef hook to get reference to the hidden input element
  const hiddenInputRef = useRef<HTMLInputElement>(null)

  /**
   * Handle the directory selection by programmatically triggering
   * the click event on the hidden file input element
   */
  const handleSelectDirectory = () => {
    if (hiddenInputRef.current) {
      hiddenInputRef.current.click()
    }
  }

  /**
   * Handle the onChange event of the hidden input to capture
   * the selected directory's path from the first file's webkitRelativePath
   */
  const handleDirectoryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    
    if (files && files.length > 0) {
      // Get the relative path from the first file
      const relativePath = files[0].webkitRelativePath
      
      // Extract the directory name by splitting the path and getting the first element
      // For example: "my-folder/file1.txt" -> "my-folder"
      const pathParts = relativePath.split('/')
      const directoryName = pathParts[0]
      
      // Format as home directory relative path (~/)
      const formattedPath = `~/${directoryName}`
      
      // Update the state with the selected directory path
      onChange(formattedPath)
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
      
      {/* Text input field that displays the selected directory path */}
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
              {/* Select Directory button that triggers the hidden input */}
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
    </Box>
  )
}