# Task: @{task-name}

## Task Metadata
- **Type**: Drupal Theme Component
- **Priority**: {priority}
- **Branch**: drupal/{branch-name}
- **Drupal Version**: {drupal_version}

## Drupal Context

### Theme Information
- **Theme Name**: {theme_name}
- **Theme Type**: custom
- **Location**: `web/themes/custom/{theme_name}/`
- **Base Theme**: {base_theme}

### Quality Gates Required
- ✅ PHPCS: Drupal coding standards compliance
- ✅ Accessibility: WCAG 2.1 AA compliance
- ✅ Browser Testing: Chrome, Firefox, Safari, Edge
- ✅ Visual Regression: Screenshot comparison (optional)

## Component Requirements

### User Story
{component_description}

### Acceptance Criteria
- [ ] Visual design matches mockups
- [ ] Responsive across breakpoints
- [ ] Accessible (WCAG 2.1 AA)
- [ ] Browser compatible
- [ ] Performance optimized

## Context Manifest

### Files in Scope
- `web/themes/custom/{theme_name}/{theme_name}.info.yml` - Theme definition
- `web/themes/custom/{theme_name}/{theme_name}.theme` - Preprocess functions and hooks
- `web/themes/custom/{theme_name}/{theme_name}.libraries.yml` - Asset libraries
- `web/themes/custom/{theme_name}/templates/` - Twig templates
- `web/themes/custom/{theme_name}/src/scss/` - SCSS source files
- `web/themes/custom/{theme_name}/src/js/` - JavaScript source files
- `web/themes/custom/{theme_name}/dist/` - Compiled assets

### Related Configuration
- `config/sync/block.*.yml` - Block placements
- `config/sync/core.entity_view_display.*.yml` - View mode configurations

### Dependencies
- **npm packages**: {npm_dependencies}
- **Drupal modules**: {module_dependencies}

## Architecture Notes

### Component Structure
- **Template**: {template_file}
- **Variables**: {twig_variables}
- **Preprocessing**: {preprocess_notes}
- **Libraries**: {library_definitions}

### Styling Approach
- **Methodology**: {css_methodology}
- **Breakpoints**: {responsive_breakpoints}
- **Variables**: {sass_variables}

### JavaScript Behavior
- **Drupal Behaviors**: {behavior_notes}
- **Dependencies**: {js_dependencies}
- **Event Handling**: {event_notes}

## Work Log

### Session {session_number} - {date}

#### Standards Compliance
- [ ] PHPCS: 0 errors, 0 warnings
- [ ] Accessibility: WCAG 2.1 AA compliant
- [ ] Browser testing: All major browsers

#### Asset Management
- [ ] SCSS compiled: `npm run build`
- [ ] JS bundled and minified
- [ ] Libraries defined in .libraries.yml
- [ ] Assets committed to git

#### Twig Templates
- [ ] Proper template inheritance
- [ ] Variables documented
- [ ] No logic in templates
- [ ] Caching metadata included

#### Accessibility
- [ ] Semantic HTML
- [ ] ARIA labels where needed
- [ ] Keyboard navigation works
- [ ] Screen reader tested

#### Responsive Design
- [ ] Mobile: Tested and working
- [ ] Tablet: Tested and working
- [ ] Desktop: Tested and working
- [ ] Large screens: Tested and working

#### Implementation Notes
{implementation_notes}

## Completion Checklist

### Code Quality
- [ ] All code follows Drupal coding standards
- [ ] No phpcs errors or warnings
- [ ] Twig templates properly formatted
- [ ] JavaScript follows Drupal.behaviors pattern

### Visual Design
- [ ] Matches design mockups
- [ ] Typography consistent with design system
- [ ] Colors match brand guidelines
- [ ] Spacing and layout correct

### Accessibility
- [ ] Semantic HTML structure
- [ ] Proper heading hierarchy
- [ ] Sufficient color contrast
- [ ] Focus indicators visible
- [ ] Screen reader friendly
- [ ] Keyboard navigable

### Performance
- [ ] Images optimized
- [ ] CSS minified for production
- [ ] JavaScript minified for production
- [ ] No unnecessary libraries loaded
- [ ] Lazy loading implemented (if applicable)

### Browser Compatibility
- [ ] Chrome: Tested and working
- [ ] Firefox: Tested and working
- [ ] Safari: Tested and working
- [ ] Edge: Tested and working
- [ ] Mobile browsers: Tested and working

### Assets
- [ ] SCSS compiled to CSS
- [ ] JavaScript bundled
- [ ] Source maps available for development
- [ ] Libraries registered in .libraries.yml
- [ ] Assets committed to version control

### Documentation
- [ ] Component documented in theme README
- [ ] Twig variables documented
- [ ] SCSS variables documented
- [ ] JavaScript behaviors documented

## Handoff Notes

### For Next Session
{handoff_notes}

### Known Issues
{known_issues}

### Next Steps
{next_steps}
