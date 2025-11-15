/**
 * Single Select Component with Input Text
 * A custom dropdown component that allows single selection from a list of options
 * with keyboard navigation, mouse interaction, and search functionality.
 * 
 * The selected option's text appears directly in the search input field
 */

class SingleSelectInputText {
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


        // Start the component setup
        this.init();
    }

    /**
     * Initialize the component - Set up all event listeners and DOM references
     */
    init() {
        // Get references to all important DOM elements
        this.input = this.container.querySelector('.single-select-input');
        this.dropdown = this.container.querySelector('.single-select-dropdown');
        this.searchInput = this.container.querySelector('.single-select-search-input');
        this.optionsContainer = this.container.querySelector('.single-select-options');
        

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

        // Set up input event listener for search functionality
        // This triggers every time the user types in the search input
        this.searchInput.addEventListener('input', (e) => {
            this.filterOptions(e.target.value); // Filter options based on what user typed
            this.updatePlaceholder(); // Update placeholder and styling
        });

        // Set up global click listener to close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                // Close dropdown and remove any highlighted options when clicking outside
                this.toggleDropdown(false);
                const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (currentHighlighted) {
                    currentHighlighted.classList.remove('highlighted');
                }                
            }
        });

        // Set up keyboard navigation for the container
        this.container.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                // Handle Tab key: close dropdown and move focus
                if (this.dropdown.classList.contains('active')) {
                    e.preventDefault();
                    const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                    if (currentHighlighted) {
                        currentHighlighted.classList.remove('highlighted');
                    }
                    this.toggleDropdown(false);
                    this.input.focus();
                } else {
                    // Allow normal tab navigation when tabbing out of the component
                    this.input.focus();
                    this.input.blur();
                    this.container.setAttribute('tabindex', '-1');
                    setTimeout(() => this.container.setAttribute('tabindex', '0'), 0);
                }
            } else if (e.key === 'Escape') {
                // Handle Escape key: close dropdown
                e.preventDefault();
                this.toggleDropdown(false);
            } else if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                // Handle arrow keys: navigate through options
                e.preventDefault();
                this.handleArrowKeys(e.key);
            } else if (e.key === 'Enter') {
                // Handle Enter key: select highlighted option or open dropdown
                if (this.dropdown.classList.contains('active')) {
                    e.preventDefault();
                    const highlightedOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
                    if (highlightedOption) {
                        const label = highlightedOption.querySelector('span').textContent;
                        this.addText(label);
                    }
                } else if((e.target !== this.searchInput) || (e.target === this.searchInput && this.searchInput.value === '' && this.selectedValue === null) ){
                    this.toggleDropdown(true); 
                }
            }
        });

        // Set up keyboard event listener for the search input
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const searchTerm = this.searchInput.value.trim().toLowerCase();
                if (searchTerm) {
                    // Find the first option that matches the search term
                    const matchingOption = Array.from(this.optionsContainer.querySelectorAll('.single-select-option'))
                        .find(option => {
                            const label = option.querySelector('span').textContent.toLowerCase();
                            return label.includes(searchTerm);
                        })
                    
                    if (matchingOption)  {
                        // Select the matching option
                        const label = matchingOption.querySelector('span').textContent;
                        this.addText(label);
                    }
                    else {
                        this.updatePlaceholder();
                        this.toggleDropdown(false);
                        this.input.focus();
                    }
                }
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
                
                // Get the option data
                const label = option[i].querySelector('span').textContent;

                // Remove highlight from any previously highlighted option
                const currentHighlighted = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (currentHighlighted) {
                    currentHighlighted.classList.remove('highlighted');
                }
    
                // Add highlight to the clicked option (commented out in this version)
                /*option[i].classList.add('highlighted');*/

                // Select this option by adding its text to the input
                this.addText(label);
            });
        }
    }

    addText(label) {
        // Set the search input value to the selected option's text
        this.searchInput.value = label;
        // Update placeholder and styling based on new selection
        this.updatePlaceholder();
        // Close the dropdown
        this.toggleDropdown(false);
        // Focus back to the main input
        this.input.focus();
    }

    updatePlaceholder() {
        // Check if the search input is empty
        if (this.searchInput.value === "") {
            // If empty: show the original placeholder and remove fillout styling
            this.searchInput.placeholder = this.options.placeholder;
            this.input.classList.remove('fillout');
            this.filterOptions('');
        } else {
            // If has content: clear placeholder and add fillout styling
            this.searchInput.placeholder = '';
            //this.filterOptions(this.searchInput.value);
            this.filterOptions('');
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

    handleGlobalKeydown = (e) => {
        
        if ((this.dropdown.classList.contains('active') || document.activeElement === this.input) && 
            !e.ctrlKey && !e.altKey && !e.metaKey && 
            (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete')) {
            
            // Focus the search input for typing
            this.searchInput.focus();
        }
    }

    handleArrowKeys(key) {
        // Get all visible options (not hidden by search filter)
        const visibleOptions = Array.from(this.optionsContainer.querySelectorAll('.single-select-option'))
            .filter(option => option.style.display !== 'none');
        
        if (visibleOptions.length === 0) return;

        // Get the currently highlighted option
        const currentOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
        let nextOption;

        if (!currentOption && key === 'ArrowDown') {
            // If no option is highlighted and arrowdown is pressed, highlight the first option
            nextOption = visibleOptions[0];
            nextOption.classList.add('highlighted');
            this.input.focus();
        } else {
            // Navigate through options based on current position
            const currentIndex = visibleOptions.indexOf(currentOption);
            if (key === 'ArrowDown' && currentIndex < visibleOptions.length-1) {
                // Move down: remove highlight from current, add to next
                currentOption.classList.remove('highlighted');
                nextOption = visibleOptions[(currentIndex + 1)];
                nextOption.classList.add('highlighted');
            } else if (key === 'ArrowUp' && currentIndex >= 1) {
                // Move up: remove highlight from current, add to previous
                currentOption.classList.remove('highlighted');
                nextOption = visibleOptions[(currentIndex - 1)];
                nextOption.classList.add('highlighted');
            }
        }

        // Scroll the highlighted option into view
        nextOption.scrollIntoView({ block: 'nearest' });
    }

    filterOptions(searchTerm) {
        // Get all option elements
        const option = this.optionsContainer.querySelectorAll('.single-select-option');
        let hasVisibleOptions = false;

        // Filter options based on search term
        for (let i = 0; i < option.length; i++) {
            const label = option[i].querySelector('span').textContent.toLowerCase();
            const matches = label.includes(searchTerm.toLowerCase());
            
            // Show or hide options based on search match
            option[i].style.display = matches ? 'flex' : 'none';
            if (matches) hasVisibleOptions = true;
        }

        
         // Remove highlight from any previously highlighted option
         const highlightedOption = this.optionsContainer.querySelector('.single-select-option.highlighted');
                if (highlightedOption) {
                    highlightedOption.classList.remove('highlighted');
                }
        
        // Show or hide dropdown based on whether there are visible options
        this.toggleDropdown(hasVisibleOptions);
    }
}

// Export the class for use in other files
if (typeof module !== 'undefined' && typeof module.exports) {
    module.exports = SingleSelectInputText;
}

