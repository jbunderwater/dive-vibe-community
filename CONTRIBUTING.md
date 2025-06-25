# Contributing to Dive Vibe Community Data

Thank you for your interest in contributing to the Dive Vibe Community Data repository! We welcome contributions from divers, travelers, and anyone passionate about sharing dive site information with the world.

## How to Contribute

### Option 1: Through the Dive Vibe App (Recommended for New Users)

The easiest way to contribute is through our web application:

1. **Visit the Dive Vibe App**
   - Go to [dive-vibe.com](https://divevibe.app) 
   - Sign in with your GitHub account

2. **Submit Your Contribution**
   - **New Dive Sites**: Use the "Add Dive Site" feature to submit new sites
   - **Destination Requests**: Use the "Request Destination" feature to suggest new destinations
   - **Issue Reports**: Use the "Report Issue" feature to report problems or suggest improvements

3. **What Happens Next**
   - Your submission will be automatically converted to a GitHub issue
   - Our team will review and process your contribution
   - You'll be credited for your contribution in the data

### Option 2: Direct GitHub Contribution (For Advanced Users)

If you're comfortable with Git and GitHub:

1. **Fork the repository**
   - Click the "Fork" button at the top right of this page to create your own copy.
2. **Clone your fork**
   - `git clone https://github.com/your-username/dive-vibe-community.git`
3. **Create a new branch**
   - `git checkout -b my-feature-branch`
4. **Make your changes**
   - Add or update dive site markdown files, destination data, or images.
   - Follow the data format and guidelines below.
5. **Commit and push your changes**
   - `git add .`
   - `git commit -m "Add new dive site: [Site Name]"`
   - `git push origin my-feature-branch`
6. **Open a Pull Request**
   - Go to your fork on GitHub and click "Compare & pull request".
   - Provide a clear description of your changes.

## What Can You Contribute?

- **New Dive Sites**: Add new dive sites with accurate information and tips.
- **Site Updates**: Improve or correct existing dive site data.
- **New Destinations**: Add new diving destinations and their metadata.
- **Images**: Contribute high-quality, properly attributed images.
- **Data Quality**: Fix typos, improve descriptions, or add missing details.
- **Bug Reports**: Report issues with existing data or the platform.

## Data Format Guidelines

### Dive Site Markdown Files
- Place new files in the appropriate `divesites/[destination]/` folder.
- Use YAML frontmatter for metadata:

  ```markdown
  ---
  name: [Site Name]
  lat: [latitude]
  lng: [longitude]
  difficulty: [beginner/intermediate/advanced]
  maxDepth: [max depth in feet]
  infoLink: [external reference link]
  addedBy: [your GitHub username]
  ---
  
  # [Site Name]
  
  [Description of the site]
  
  ## Tips
  - [Tip 1]
  - [Tip 2]
  ```

- Keep descriptions concise but informative.
- Add tips, marine life info, and entry/exit notes if possible.

### Destination Data
- Add new destinations to `destinations.json`.
- Include:
  - `name`, `slug`, `center`, `bounds`, `description`

### Images
- Place images in the `images/` directory or appropriate subfolder.
- Only upload images you have rights to share.
- Add attribution in the image filename or a separate credits file.

## App-Based Contribution Guidelines

When contributing through the app:

### For New Dive Sites
- Provide accurate GPS coordinates
- Include difficulty level and maximum depth
- Add a detailed description of the site
- Mention notable marine life and features
- Include tips for visiting divers

### For Destination Requests
- Provide the destination name and location
- Include a brief description of why it should be added
- Mention any notable dive sites in the area

### For Issue Reports
- Be specific about what needs to be fixed
- Include screenshots if relevant
- Provide context about when you encountered the issue

## Code of Conduct

Be respectful and constructive. We value a welcoming and inclusive community.

## Review Process

- All submissions (both app-based and direct GitHub contributions) are reviewed by maintainers.
- We may request changes or clarifications before merging.
- Once approved, your contribution will be merged and credited.
- For app-based contributions, you'll receive updates via GitHub notifications.

## Questions?

- Open an issue for help or suggestions.
- Join our [Discussions](https://github.com/your-org/dive-vibe-community/discussions) for community support.
- Contact us through the app's support features.

---

Thank you for helping make Dive Vibe better for divers everywhere! 