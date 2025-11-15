/**
 * Single Select Component
 * A custom dropdown component that allows single selection from a list of options
 * with keyboard navigation, mouse interaction, and search functionality.
 */

class SingleSelect {
    constructor(containerID, options = {}) {
        // Get the main container element by its ID
        this.container = document.getElementById(containerID);
        
        // Initialize component options with defaults
        this.options = {
            placeholder: options.placeholder,
            searchable: options.searchable !== false, // Default to true unless explicitly set to false
            onChange: options.onChange || (() => {}), // Callback function when selection changes
            data: options.data || [] // Array of data options
        };

        // Track the currently selected value
        this.selectedValue = null;
        
        // Initialize the component
        this.init();
    }

    init() {
        // Get references to all important DOM elements
        this.input = this.container.querySelector('.single-select-input');
        this.dropdown = this.container.querySelector('.single-select-dropdown');
        this.searchInput = this.container.querySelector('.single-select-search-input');
        this.optionsContainer = this.container.querySelector('.single-select-options');

        // disable search funcionality based on inicialitation component options
        if (this.options.searchable === false) {
            this.searchInput.readOnly = true;
        }
        
        

        // Make the container focusable for keyboard navigation
        // Set tabindex to -1 on child elements to prevent them from receiving focus during tab navigation
        this.container.setAttribute('tabindex', '0');
        this.input.setAttribute('tabindex', '-1');
        this.searchInput.setAttribute('tabindex', '-1');
       
        
        // Set up the dropdown options and their event listeners
        this.setupOptions();

        // Set up focus event listener for the container
        this.container.addEventListener('focus', () => {
            // If dropdown is closed and no value is selected, focus the search input
            if(!this.dropdown.classList.contains('active') && this.selectedValue === null) {
                this.searchInput.focus();
            }
            else {
                // Otherwise focus the main input
                this.input.focus();
            }
        });

        // Set up focus event listener for the input
        this.input.addEventListener('focus', () => {
            // Add global keydown listener when input is focused
            document.addEventListener('keydown', this.handleGlobalKeydown);
        });

        // Set up click event listeners for both input and search input
        [this.input, this.searchInput].forEach(element => {
            element.addEventListener('click', (e) => {
                // Open the dropdown when clicking on input or search input
                this.toggleDropdown(true);
            });
        });

        // Set up global click listener to close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                // Close dropdown and remove any highlighted options
                this.toggleDropdown(false);
                const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
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
                    const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                    if (currentHighlighted) {
                        currentHighlighted.classList.remove('highlighted');
                    }
                    this.toggleDropdown(false);
                    //this.input.focus();
                } else {
                    // Allow normal tab navigation when tabbing out of the component
                    this.input.focus();
                    this.input.blur();
                    this.container.setAttribute('tabindex', '-1');
                    setTimeout(() => this.container.setAttribute('tabindex', '0'), 0);
                }
            // Escape: Close dropdown
            } else if (e.key === 'Escape') {
                e.preventDefault();
                this.toggleDropdown(false);
            // Arrow keys: Navigate through options
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.handleArrowKeys(e.key);
            // Enter: Select highlighted option or open dropdown
            } else if (e.key === 'Enter') {
                if (this.dropdown.classList.contains('active')) {
                    e.preventDefault();
                    const highlightedOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
                    if (highlightedOption) {
                        const checkbox = highlightedOption.querySelector('input[type="checkbox"]');
                        const value = checkbox.value;
                        const label = highlightedOption.querySelector('span').textContent;
                        this.toggleOption(value, label);
                    }
                } else if((e.target !== this.searchInput) || (e.target === this.searchInput && this.searchInput.value === '' && this.selectedValue === null) ){
                    this.toggleDropdown(true); 
                }
            } else if ((e.key === 'Delete' || e.key === 'Backspace') && this.searchInput.value === '') {
                e.preventDefault();
                this.removeText();
                this.input.focus();
            }
        });

    }

    setupOptions() {
        // Get all option elements from the dropdown
        const option = this.optionsContainer.querySelectorAll('.single-select-option');
        
        // Set up hover interaction for each option
        for (let i = 0; i < option.length; i++) {
            // Add mouseenter event listener for hover effect
            option[i].addEventListener('mouseenter', () => {
                // Remove highlight from any previously highlighted option
                const highlightedOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (highlightedOption) {
                    highlightedOption.classList.remove('highlighted');
                }
                // Add highlighted class to the option under mouse cursor
                option[i].classList.add('highlighted');
            })

            // Add mouseleave event listener to remove highlight when mouse leaves
            option[i].addEventListener('mouseleave', () => {
                option[i].classList.remove('highlighted');
            })
        }

        // Set up click interaction for each option
        for (let i = 0; i < option.length; i++) {
            option[i].addEventListener('click', (e) => {
                e.stopPropagation();
                
                // Get the checkbox and option data
                const checkbox = option[i].querySelector('input[type="checkbox"]');
                const value = checkbox.value;
                const label = option[i].querySelector('span').textContent;

                // Remove highlight from any previously highlighted option
                const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (currentHighlighted) {
                    currentHighlighted.classList.remove('highlighted');
                }
    
                // Add highlight to the clicked option
                option[i].classList.add('highlighted');

                // Toggle the selection (select this option)
                this.toggleOption(value, label);
            });
        }
    }

    
    toggleOption(value, label) {
        // Get references to the checkbox and option element being selected
        const newCheckbox = this.optionsContainer.querySelector(`input[value="${value}"]`);
        const newOption = newCheckbox?.closest('.single-select-option');

        // Only update if the value is different from the currently selected value
        if (this.selectedValue !== value) {
            // Remove the current selection first
            this.removeText();
            
            // Set the new selection
            this.selectedValue = value;
            this.addText(value, label);
            
            // Update the checkbox and option visual state
            if (newCheckbox && newOption) {
                newCheckbox.checked = true;
                newOption.classList.add('selected');
            }
        }
        
        // Update the component state
        this.updatePlaceholder();
        this.options.onChange(this.selectedValue);
        
        // Clear search and close dropdown
        this.searchInput.value = '';
        //this.filterOptions('');
        this.toggleDropdown(false);
        this.input.focus();
        this.searchInput.style.display = 'none';
    }

    addText(value, label) {
        // Prevent adding duplicate values
        if (this.input.querySelector(`[data-value="${value}"]`)) {
            return;
        }
        
        // Create a new text element to display the selected option
        const text = document.createElement('span');
        text.className = 'single-select-text';
        text.dataset.value = value;
        text.textContent = label;

        // Insert the text before the search input in the container
        this.input.querySelector('.single-select-text-container').insertBefore(text, this.searchInput);
    }

    removeText() {
        // Get references to the current selection
        const currentCheckbox = this.optionsContainer.querySelector(`input[value="${this.selectedValue}"]`);
        const currentOption = currentCheckbox?.closest('.single-select-option');

        if (currentCheckbox && currentOption) {
            
            const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (currentHighlighted) {
                    currentHighlighted.classList.remove('highlighted');
                }
            // Uncheck the checkbox and remove selected class
            currentCheckbox.checked = false;
            currentOption.classList.remove('selected');

            // Remove the text element from the input
            const text = this.input.querySelector(`.single-select-text[data-value="${this.selectedValue}"]`);
            if (text) {
                text.remove();
            }
        }

        // Reset the component state
        this.selectedValue = null;
        this.updatePlaceholder();
        this.options.onChange(null);
        this.searchInput.style.display = 'flex';
    }

    updatePlaceholder() {
        // Update the placeholder text based on whether a value is selected
        const placeholder = this.searchInput.placeholder;
        if (this.selectedValue === null) {
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
        // Check if dropdown was closed before this call
        const wasClosed = !this.dropdown.classList.contains('active');
        
        // Toggle the dropdown visibility
        if (typeof show === 'boolean') {
            // Force the dropdown to be open (true) or closed (false)
            this.dropdown.classList.toggle('active', show);
        } else {
            // Toggle the current state (open if closed, close if open)
            this.dropdown.classList.toggle('active');
        }
        
        // If the dropdown just opened (was closed before, and now is open now)
        if (wasClosed && this.dropdown.classList.contains('active')) {
            // Highlight the currently selected option when opening
            const selected = this.optionsContainer.querySelector('.single-select-option.selected');
            if (selected) {
                selected.classList.add('highlighted');
            }
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
            
            // Focus the search input for typing
            this.searchInput.focus();
        }
    }

    handleArrowKeys(key) {
        // Get all options
        const options = Array.from(this.optionsContainer.querySelectorAll('.single-select-option'));
        
        if (options.length === 0) return;

        // Get the currently highlighted option
        const currentOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
        let nextOption;

        if (!currentOption && key === 'ArrowDown') {
            // If no option is highlighted and arrowdown is pressed, highlight the first option
            nextOption = options[0];
            nextOption.classList.add('highlighted');
            this.input.focus();
        } else {
            // Navigate through options based on current position
            const currentIndex = options.indexOf(currentOption);
            if (key === 'ArrowDown' && currentIndex < options.length-1) {
                // Move down: remove highlight from current, add to next
                currentOption.classList.remove('highlighted');
                nextOption = options[(currentIndex + 1)];
                nextOption.classList.add('highlighted');
            } else if (key === 'ArrowUp' && currentIndex >= 1) {
                // Move up: remove highlight from current, add to previous
                currentOption.classList.remove('highlighted');
                nextOption = options[(currentIndex - 1)];
                nextOption.classList.add('highlighted');
            }
        }

        // Scroll the highlighted option into view
        nextOption.scrollIntoView({ block: 'nearest' });
    }

    // Programmatically set selected value
    // Useful for pre-populating the component
    setValue(value) {
        this.removeText();

        const checkbox = this.optionsContainer.querySelector(`input[value="${value}"]`);
        if (checkbox) {
            const label = checkbox.closest('.single-select-option').querySelector('span').textContent;
            this.toggleOption(value, label);
        }
    }
    
}

// Export the class for use in other files
if (typeof module !== 'undefined' && typeof module.exports) {
    module.exports = SingleSelect;
}

