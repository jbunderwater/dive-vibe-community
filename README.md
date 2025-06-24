# Dive Vibe Community Data

Welcome to the Dive Vibe Community Data repository! This repository serves as the central data store for dive site information, destinations, and community-contributed content for the Dive Vibe platform.

## 🏊‍♂️ What is Dive Vibe?

Dive Vibe is a community-driven platform that helps divers discover and share information about dive sites around the world. This repository contains all the structured data that powers the Dive Vibe application, including dive site details, destination information, and community contributions.

## 📁 Repository Structure

```
dive-vibe-community/
├── destinations.json          # List of dive destinations with metadata
├── divesites/                 # Individual dive site data organized by destination
│   └── [destination]/         # e.g., bonaire/
│       ├── index.json         # List of dive sites for this destination
│       └── [site-name].md     # Individual dive site markdown files
├── images/                    # Dive site and destination images
├── schemas/                   # Data validation schemas (future)
└── .github/                   # GitHub workflows and templates
```

## 🗺️ Data Organization

### Destinations (`destinations.json`)
Each destination entry contains:
- `name`: Human-readable destination name
- `slug`: URL-friendly identifier
- `center`: [latitude, longitude] for map centering
- `bounds`: [[south, west], [north, east]] for map boundaries
- `description`: Brief description of the destination

### Dive Sites
Dive sites are organized by destination in the `divesites/` directory:

#### Destination Index (`divesites/[destination]/index.json`)
Contains metadata for all dive sites in a destination:
- `name`: Dive site name
- `lat`/`lng`: GPS coordinates
- `filename`: Corresponding markdown file
- `infoLink`: External reference link
- `addedBy`: Contributor username
- `difficulty`: beginner/intermediate/advanced
- `maxDepth`: Maximum depth in feet

#### Individual Site Files (`divesites/[destination]/[site-name].md`)
Markdown files with frontmatter containing:
- Site metadata (coordinates, difficulty, etc.)
- Detailed description
- Tips and recommendations
- Marine life information
- Entry/exit details

## 🤝 Contributing

We welcome contributions from the diving community! Whether you're adding new dive sites, updating existing information, or improving data quality, your contributions help make Dive Vibe better for everyone.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch** for your changes
3. **Add or update dive site data** following our data format
4. **Submit a pull request** with a clear description of your changes

### What You Can Contribute

- **New dive sites**: Add information about dive sites not yet in our database
- **Site updates**: Improve existing dive site information with more details
- **New destinations**: Add entire new diving destinations
- **Data quality**: Fix errors, improve descriptions, or add missing information
- **Images**: Contribute high-quality photos of dive sites (with proper attribution)

### Data Guidelines

- **Accuracy**: Ensure all information is accurate and up-to-date
- **Completeness**: Provide as much detail as possible while keeping it concise
- **Attribution**: Credit sources when using information from other websites
- **Consistency**: Follow the established data format and naming conventions

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📊 Current Coverage

- **Destinations**: 2 destinations (Bonaire, Curacao)
- **Dive Sites**: 4 dive sites in Bonaire
- **Contributors**: Community-driven with sample data


## 📝 License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/your-org/dive-vibe-community/issues)
- **Discussions**: Join community discussions in [GitHub Discussions](https://github.com/your-org/dive-vibe-community/discussions)
- **Documentation**: Check our [Wiki](https://github.com/your-org/dive-vibe-community/wiki) for detailed guides

## 🙏 Acknowledgments

Thank you to all the divers, dive operators, and community members who contribute their knowledge and experiences to make this platform possible. Every contribution helps fellow divers discover amazing underwater experiences around the world.

---

**Happy Diving! 🐠🐙🦈** 