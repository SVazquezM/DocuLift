/**
 * MultiSelect Component
 * 
 * A customizable multi-select dropdown component with search functionality.
 * Features:
 * - Multiple selection with visual tags
 * - Real-time search/filtering
 * - Keyboard navigation (Arrow keys, Enter, Escape, Tab)
 */

class MultiSelect {
            constructor(containerId, options = {}) {
                // Get the main container element by its ID
                this.container = document.getElementById(containerId);
                // Initialize component options with defaults
                this.options = {
                    placeholder: options.placeholder ,
                    searchable: options.searchable !== false, // Default to true unless explicitly set to false
                    maxSelection: options.maxSelection || null, // Default to null unless explicitly set
                    onChange: options.onChange || (() => {}), // Callback function when selection changes
                    data: options.data || [] // Array of data options
                };

                // Track the currently selected values
                this.selectedValues = new Set();
                // Initialize the component
                this.init();
            }

           
            init() {
                // Get references to all important DOM elements
                this.input = this.container.querySelector('.multi-select-input');
                this.dropdown = this.container.querySelector('.multi-select-dropdown');
                this.searchInput = this.container.querySelector('.multi-select-search-input');
                this.optionsContainer = this.container.querySelector('.multi-select-options');
                this.clearAllBtn = this.container.querySelector('.multi-select-clear-all');

                // Make container focusable for keyboard navigation
                // Set tabindex to -1 on child elements to prevent them from receiving focus during tab navigation
                this.container.setAttribute('tabindex', '0');
                this.input.setAttribute('tabindex', '-1');
                this.searchInput.setAttribute('tabindex', '-1');
                this.clearAllBtn.setAttribute('tabindex', '-1');

                // Configure dropdown options and their event listeners
                this.setupOptions();

                // Set up focus event listener for the container
                this.container.addEventListener('focus', () => {
                    // If dropdown is closed, focus the search input
                   if(!this.dropdown.classList.contains('active')) {
                        this.searchInput.focus();
                    }
                    
                });

                // Set up click event listeners for both input and search input to open the dropdownwhen clicking on them
                [this.input, this.searchInput].forEach(element => {
                    element.addEventListener('click', (e) => {
                        // Clear any highlighted option when clicking
                        const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                        if (currentHighlighted) {
                            currentHighlighted.classList.remove('highlighted');
                        }

                        // Prevents opening if user clicks on a remove-tag button
                        if (e.target.closest('.remove-tag')) {
                            return;
                        }

                        // Open the dropdown
                        this.toggleDropdown(true);
                    });
                });

                 // Set up input event listener for search functionality
                this.searchInput.addEventListener('input', (e) => this.filterOptions(e.target.value));
                
                // Set up global click listener to close dropdown when clicking outside
                document.addEventListener('click', (e) => {
                    if (!this.container.contains(e.target)) {
                        // Close dropdown and remove any highlighted options
                        this.toggleDropdown(false);
                        const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                        if (currentHighlighted) {
                            currentHighlighted.classList.remove('highlighted');
                        }
                       
                        
                    }
                });

                // Set up keyboard navigation for the container
                this.container.addEventListener('keydown', (e) => {
                    // Tab key: Close dropdown and manage focus
                    if (e.key === 'Tab') {
                        if (this.dropdown.classList.contains('active')) {
                            e.preventDefault();
                            const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                            if (currentHighlighted) {
                                currentHighlighted.classList.remove('highlighted');
                            }
                            
                            this.toggleDropdown(false);
                            document.addEventListener('keydown', this.handleGlobalKeydown);                            
                           
                        
                        } else {
                            // Allow normal tab navigation when tabbing out of the component
                            this.input.focus();
                            this.input.blur();
                            this.container.setAttribute('tabindex', '-1');
                            setTimeout(() => this.container.setAttribute('tabindex', '0'), 0);
                        }
                        
                    // Arrow keys: Navigate through options
                    } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                        e.preventDefault();
                        this.handleArrowKeys(e.key);
                    // Escape: Close dropdown
                    } else if (e.key === 'Escape') {
                        e.preventDefault();
                        this.toggleDropdown(false);
                    // Enter: Select highlighted option or open dropdown
                    } else if (e.key === 'Enter') {
                        if (this.dropdown.classList.contains('active')) {
                            e.preventDefault();
                            const highlightedOption = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                            if (highlightedOption) {
                                const checkbox = highlightedOption.querySelector('input[type="checkbox"]');
                                const value = checkbox.value;
                                const label = highlightedOption.querySelector('span').textContent;
                                this.toggleOption(value, label);
                            }
                        } else {
                            this.toggleDropdown(true);
                        }
                    } 
                });

                // Search input keyboard handlers
                this.searchInput.addEventListener('keydown', (e) => {
                    // Enter: Select first matching option from search
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const searchTerm = this.searchInput.value.trim().toLowerCase();
                        if (searchTerm) {
                            // Find first option that matches the search term
                            const matchingOption = Array.from(this.optionsContainer.querySelectorAll('.multi-select-option'))
                                .find(option => {
                                    const label = option.querySelector('span').textContent.toLowerCase();
                                    return label.includes(searchTerm);
                                });

                            if (matchingOption) {
                                const checkbox = matchingOption.querySelector('input[type="checkbox"]');
                                const value = checkbox.value;
                                const label = matchingOption.querySelector('span').textContent;
                                this.toggleOption(value, label);
                                this.searchInput.value = '';
                                this.filterOptions('');
                            }
                        }
                    }
                    // Delete/Backspace on empty input: Remove last selected tag
                    else if (e.key === 'Delete' && this.searchInput.value === '') {
                        e.preventDefault();
                        this.removeLastTag();
                    } else if (e.key === 'Backspace' && this.searchInput.value === '') {
                        e.preventDefault();
                        this.removeLastTag();
                    }
                });

                // Clear all button: Remove all selections
                this.clearAllBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.clearAll();
                    this.searchInput.focus();
                });
            }

            
            setupOptions() {
                // Get all option elements from the dropdown
                this.optionsContainer.querySelectorAll('.multi-select-option').forEach(option => {
                    // Add click event listener for each option
                    option.addEventListener('click', (e) => {
                        e.stopPropagation();
                        this.searchInput.blur();

                        // Get the checkbox and option data
                        const checkbox = option.querySelector('input[type="checkbox"]');
                        const value = checkbox.value;
                        const label = option.querySelector('span').textContent;
                        
                        // Remove highlight from any previously highlighted option
                        const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                        if (currentHighlighted) {
                            currentHighlighted.classList.remove('highlighted');
                        }
                        
                        // Add highlight to the clicked option
                        option.classList.add('highlighted');
                        
                        // Toggle the selection (select this option)
                        this.toggleOption(value, label);
                        
                    });
                });

            }

            
            toggleOption(value, label) {
                // Get references to the checkbox and option element being selected
                const checkbox = this.optionsContainer.querySelector(`input[value="${value}"]`);
                const option = checkbox.closest('.multi-select-option');
                
                if (this.selectedValues.has(value)) {
                    // If the value is already selected, remove it
                    this.selectedValues.delete(value);
                    this.removeTag(value);
                    if (checkbox) {
                        checkbox.checked = false;
                        option.classList.remove('selected');
                    }
                } else {
                    // If the value is not selected, check maxSelection limit before adding
                    if (this.options.maxSelection && this.selectedValues.size >= this.options.maxSelection) {
                        return;
                    }
                    this.selectedValues.add(value);
                    this.addTag(value, label);
                    if (checkbox) {
                        checkbox.checked = true;
                        option.classList.add('selected');
                    }
                }

                this.updatePlaceholder();
                this.updateClearAllButton();
                // Trigger onChange callback with array of selected values
                this.options.onChange(Array.from(this.selectedValues));
            }

          
            addTag(value, label) {
                // If the value already exists, do not add it again (prevent duplicates)
                if (this.input.querySelector(`[data-value="${value}"]`)) {
                    return;
                }

                // Create tag element
                const tag = document.createElement('span');
                tag.className = 'multi-select-tag';
                tag.dataset.value = value;
                
                // Create label text safely (prevents XSS)
                const labelSpan = document.createElement('span');
                labelSpan.textContent = label;
                
                // Create remove button (×)
                const removeTag = document.createElement('span');
                removeTag.className = 'remove-tag';
                removeTag.textContent = '×';
                
                // Assemble tag structure
                tag.appendChild(labelSpan);
                tag.appendChild(removeTag);

                // Add click handler to remove button
                tag.querySelector('.remove-tag').addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleOption(value, label);
                    const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                        if (currentHighlighted) {
                            currentHighlighted.classList.remove('highlighted');
                        }
                });

                // Insert tag before the search input
                this.input.querySelector('.multi-select-tags-container').insertBefore(tag, this.searchInput);
            }

            removeTag(value) {
                // Get the tag element with the corresponding value
                const tag = this.input.querySelector(`[data-value="${value}"]`);
                // If the tag exists, remove it
                if (tag) {
                    tag.remove();
                }
            }

            updatePlaceholder() {
                // Update the placeholder text based on whether a value is selected
                const placeholder = this.searchInput.placeholder;
                if (this.selectedValues.size === 0) {
                    // Show the original placeholder when no value is selected
                    this.searchInput.placeholder = this.options.placeholder;
                    this.input.classList.remove('fillout');
                } else {
                    // Clear placeholder when a value is selected
                    this.searchInput.placeholder = '';
                    this.input.classList.add('fillout');
                }
            }

            toggleDropdown(show) {
                // Toggle the dropdown visibility
                if (typeof show === 'boolean') {
                     // Force the dropdown to be open (true) or closed (false)
                    this.dropdown.classList.toggle('active', show);
                } else {
                    // Toggle the current state (open if closed, close if open)
                    this.dropdown.classList.toggle('active');
                }

                // Update the input state and focus based on dropdown status
                if (this.dropdown.classList.contains('active')) {
                    // Dropdown is open: add active class, focus search input, add global keydown listener
                    this.input.classList.add('active');
                    this.searchInput.focus();
                    document.addEventListener('keydown', this.handleGlobalKeydown);
                } else {
                     // Dropdown is closed: remove active class, remove global keydown listener
                    this.input.classList.remove('active');
                    document.removeEventListener('keydown', this.handleGlobalKeydown);
                }
            }

            // Global keyboard handler - Redirects typing to search input when dropdown is active
            handleGlobalKeydown = (e) => {
            
                if ((this.dropdown.classList.contains('active') || document.activeElement === this.input) && 
                    !e.ctrlKey && !e.altKey && !e.metaKey && 
                    (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete')) {
                    
                    this.searchInput.focus();
                }
            }

            
            handleArrowKeys(key) {
                // Get only visible options (not filtered out by search)
                const visibleOptions = Array.from(this.optionsContainer.querySelectorAll('.multi-select-option'))
                    .filter(option => option.style.display !== 'none');
                
                if (visibleOptions.length === 0) return;

                // Get the currently highlighted option
                const currentOption = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                let nextOption;

                // If no option is highlighted and ArrowDown is pressed, highlight first option
                if (!currentOption && key === 'ArrowDown') {
                    nextOption = visibleOptions[0];
                    nextOption.classList.add('highlighted');
                    this.input.focus();
                } else {
                    // Navigate up or down from current position
                    const currentIndex = visibleOptions.indexOf(currentOption);
                    // ArrowDown: Move to next option (if not at end)
                    if (key === 'ArrowDown' && currentIndex < visibleOptions.length-1) {
                        nextOption = visibleOptions[(currentIndex + 1)];
                        currentOption.classList.remove('highlighted');
                        nextOption.classList.add('highlighted');
                    // ArrowUp: Move to previous option (if not at start)
                    } else if (key === 'ArrowUp' && currentIndex >= 1) {
                        nextOption = visibleOptions[(currentIndex - 1)];
                        currentOption.classList.remove('highlighted');
                        nextOption.classList.add('highlighted');
                    }
                }

                // Scroll highlighted option into view if it exists
                if (nextOption) {
                    nextOption.scrollIntoView({ block: 'nearest' });
                }
            }

            /**
             * Filter dropdown options based on search term
             * Shows only options that match the search term (case-insensitive)
             */
            filterOptions(searchTerm) {
                const options = this.optionsContainer.querySelectorAll('.multi-select-option');
                let hasVisibleOptions = false;

                // Show/hide options based on search match
                options.forEach(option => {
                    const label = option.querySelector('span').textContent.toLowerCase();
                    const matches = label.includes(searchTerm.toLowerCase());
                    option.style.display = matches ? 'flex' : 'none';
                    if (matches) hasVisibleOptions = true;
                });

                // Clear highlighted option when filtering (prevents highlighting hidden options)
                const highlightedOption = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                if (highlightedOption) {
                    highlightedOption.classList.remove('highlighted');
                }

                // Show dropdown only if there are visible options
                this.toggleDropdown(hasVisibleOptions);
            }

            /**
             * Clear all selected options
             * Removes all tags, unchecks all checkboxes, and resets the component state
             */
            clearAll() {
                // Uncheck all checkboxes and remove selection styling
                this.optionsContainer.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                    checkbox.checked = false;
                    checkbox.closest('.multi-select-option').classList.remove('selected');
                    checkbox.closest('.multi-select-option').classList.remove('highlighted');
                });
                
                // Remove all visual tags from the input
                this.input.querySelectorAll('.multi-select-tag').forEach(tag => {
                    tag.remove();
                });
                
                // Clear the Set of selected values
                this.selectedValues.clear();
                
                // Update placeholder and clear all button visibility
                this.updatePlaceholder();
                this.updateClearAllButton();
                
                // Trigger onChange callback with empty array
                this.options.onChange([]);
            }

            // Programmatically set selected values
            // Useful for pre-populating the component
            setValues(values) {
                // Clear current selections first
                this.clearAll();
                
                // Select each value in the provided array
                values.forEach(value => {
                    const checkbox = this.optionsContainer.querySelector(`input[value="${value}"]`);
                    if (checkbox) {
                        const label = checkbox.closest('.multi-select-option').querySelector('span').textContent;
                        this.toggleOption(value, label);
                    }
                });
            }

            // Update the visibility of the "clear all" button
            // Shows the button only when there are selected values
            updateClearAllButton() {
                this.clearAllBtn.classList.toggle('visible', this.selectedValues.size > 0);
            }

            // Remove the last selected tag
            // Called when user presses Delete/Backspace on empty search input
            removeLastTag() {
                const tags = this.input.querySelectorAll('.multi-select-tag');
                if (tags.length > 0) {
                    const lastTag = tags[tags.length - 1];
                    const value = lastTag.dataset.value;
                    const label = lastTag.textContent.trim();
                    this.toggleOption(value, label);

                    const currentHighlighted = this.optionsContainer.querySelector('.multi-select-option.highlighted');
                    if (currentHighlighted) {
                        currentHighlighted.classList.remove('highlighted');
                    }
                }
            }
        }

// Export the class for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MultiSelect;
} 