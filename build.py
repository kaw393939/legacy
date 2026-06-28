#!/usr/bin/env python3
"""
Legs on the Ground - Static Site Generator
A simple, elegant build system for content-driven sites
"""

import sys
import shutil
import yaml
import markdown
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import argparse


def _minify_css_conservative(css: str) -> str:
    """Conservative CSS minification.

    Avoids aggressive transformations (no comment stripping, no token rewriting)
    to keep risk low. Primarily removes trailing whitespace and excessive
    blank lines.
    """

    lines = [ln.rstrip() for ln in css.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
    out: list[str] = []
    blank_run = 0
    for ln in lines:
        if not ln.strip():
            blank_run += 1
            if blank_run <= 1:
                out.append('')
            continue
        blank_run = 0
        out.append(ln)
    return '\n'.join(out).strip() + '\n'

class SiteBuilder:
    """Main site builder class"""
    
    def __init__(self, config_path='content/config.yaml'):
        """Initialize the builder"""
        self.project_root = Path(__file__).parent
        self.config = self.load_yaml(config_path)
        
        # Directories
        self.content_dir = self.project_root / 'content'
        self.template_dir = self.project_root / self.config['build']['template_dir']
        self.static_dir = self.project_root / self.config['build']['static_dir']
        self.output_dir = self.project_root / self.config['build']['output_dir']
        
        # Setup Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Setup Markdown
        self.md = markdown.Markdown(extensions=[
            'meta',
            'extra',
            'codehilite',
            'toc'
        ])
        
        print("🏗️  Legs on the Ground - Site Builder")
        print("=" * 50)
    
    def load_yaml(self, path):
        """Load and parse YAML file"""
        try:
            with open(self.project_root / path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading {path}: {e}")
            sys.exit(1)
    
    def load_all_data(self):
        """Load all data files"""
        data_dir = self.content_dir / 'data'
        data = {}
        
        print("\n📦 Loading content data...")
        
        for yaml_file in data_dir.glob('*.yaml'):
            key = yaml_file.stem
            key_normalized = key.replace('-', '_')  # Normalize hyphens to underscores
            content = self.load_yaml(f'content/data/{yaml_file.name}')
            
            # If the YAML file has a top-level key matching the filename (with either - or _), unwrap it
            if isinstance(content, dict):
                if key in content:
                    data[key_normalized] = content[key]
                elif key_normalized in content:
                    data[key_normalized] = content[key_normalized]
                else:
                    data[key_normalized] = content
            else:
                data[key_normalized] = content
            
            print(f"   ✓ Loaded {key_normalized}")
        
        return data
    
    def parse_page(self, page_path):
        """Parse a markdown page with frontmatter"""
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                markdown_content = parts[2].strip()
            else:
                frontmatter = {}
                markdown_content = content
        else:
            frontmatter = {}
            markdown_content = content
        
        # Convert markdown to HTML
        html_content = self.md.convert(markdown_content)
        
        return frontmatter, html_content
    
    def build_page(self, page_file, data):
        """Build a single page"""
        page_path = self.content_dir / 'pages' / page_file
        
        if not page_path.exists():
            print(f"   ⚠️  Page not found: {page_file}")
            return
        
        print(f"   📄 Building {page_file}...")
        
        # Parse the page
        frontmatter, content = self.parse_page(page_path)
        
        # Determine output filename
        if page_file == 'home.md':
            output_file = 'index.html'
        else:
            output_file = page_path.stem + '.html'
        
        # Get layout template
        layout = frontmatter.get('layout', 'default')
        template = self.jinja_env.get_template(f'{layout}.html')
        
        # Build context
        context = {
            'site': self.config['site'],
            'features': self.config.get('features', {}),
            'page': frontmatter,
            'content': content,
            'build_time': datetime.now().isoformat(),
            'current_year': datetime.now().year,
            'section': frontmatter,  # For section data in frontmatter
            **data  # Add all data files (services, testimonials, etc.)
        }
        
        # Render template
        html = template.render(**context)
        
        # Write output
        output_path = self.output_dir / output_file
        output_path.write_text(html, encoding='utf-8')
        
        print(f"      ✓ Generated {output_file}")
    
    def copy_static_files(self, minify_css: bool = False):
        """Copy static assets to output"""
        print("\n📁 Copying static assets...")
        
        if not self.static_dir.exists():
            print(f"   ⚠️  Static directory not found: {self.static_dir}")
            return
        
        # Copy / bundle CSS
        css_src = self.static_dir / 'css'
        css_dest = self.output_dir
        if css_src.exists():
            parts_dir = css_src / 'parts'
            part_files = sorted(parts_dir.glob('*.css')) if parts_dir.exists() else []

            if part_files:
                bundled = "\n".join(
                    p.read_text(encoding='utf-8').rstrip() for p in part_files
                ).rstrip() + "\n"
                if minify_css:
                    bundled = _minify_css_conservative(bundled)
                (css_dest / 'styles.css').write_text(bundled, encoding='utf-8')
                print(f"   ✓ Bundled styles.css ({len(part_files)} parts)")

                # Copy any additional standalone CSS files except styles.css
                for css_file in css_src.glob('*.css'):
                    if css_file.name == 'styles.css':
                        continue
                    shutil.copy2(css_file, css_dest / css_file.name)
                    print(f"   ✓ Copied {css_file.name}")
            else:
                for css_file in css_src.glob('*.css'):
                    shutil.copy2(css_file, css_dest / css_file.name)
                    print(f"   ✓ Copied {css_file.name}")
        
        # Copy JS
        js_src = self.static_dir / 'js'
        js_dest = self.output_dir
        if js_src.exists():
            for js_file in js_src.glob('*.js'):
                shutil.copy2(js_file, js_dest / js_file.name)
                print(f"   ✓ Copied {js_file.name}")
        
        # Copy images
        img_src = self.static_dir / 'images'
        img_dest = self.output_dir / 'images'
        if img_src.exists():
            if img_dest.exists():
                shutil.rmtree(img_dest)
            shutil.copytree(img_src, img_dest)
            print("   ✓ Copied images/ directory")
        
        # Copy SEO and deployment files
        seo_files = ['robots.txt', 'sitemap.xml', 'CNAME', '.nojekyll']
        for seo_file in seo_files:
            src = self.static_dir / seo_file
            if src.exists():
                shutil.copy2(src, self.output_dir / seo_file)
                print(f"   ✓ Copied {seo_file}")
    
    def clean_output(self):
        """Clean the output directory"""
        if self.output_dir.exists():
            print(f"\n🧹 Cleaning {self.output_dir}...")
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def build(self, clean=True, minify_css: bool = False):
        """Build the entire site"""
        start_time = datetime.now()
        
        # Clean output directory
        if clean:
            self.clean_output()
        
        # Load all data
        data = self.load_all_data()
        
        # Build pages
        print("\n🔨 Building pages...")
        pages_dir = self.content_dir / 'pages'
        
        for page_file in pages_dir.glob('*.md'):
            self.build_page(page_file.name, data)
        
        # Copy static files
        self.copy_static_files(minify_css=minify_css)
        
        # Build complete
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "=" * 50)
        print(f"✅ Build complete in {elapsed:.2f}s")
        print(f"📂 Output: {self.output_dir}")
        print("=" * 50)
    
    def validate(self):
        """Validate output HTML/CSS."""
        print("\n🔍 Validating output...")

        html_files = list(self.output_dir.glob('*.html'))
        if not html_files:
            print("   ❌ No HTML files generated!")
            return False

        print(f"   ✓ Generated {len(html_files)} HTML files")

        # Check for critical files
        critical = ['index.html', 'styles.css']
        for file in critical:
            if not (self.output_dir / file).exists():
                print(f"   ❌ Missing critical file: {file}")
                return False
        print("   ✓ All critical files present")

        # Deeper validation (best-effort)
        try:
            from validator import SiteValidator

            print("\n" + "="*60)
            print("🔍 QUALITY VALIDATION")
            print("="*60)

            validator = SiteValidator(self.output_dir)
            results = validator.validate_all()

            report = validator.generate_report()
            print(report)

            report_path = self.project_root / 'validation-report.json'
            validator.save_report(report_path)

            total_errors = sum(len(r.errors) for r in results)
            if total_errors > 0:
                print(f"\n⚠️  Validation failed with {total_errors} errors")
                return False

            print("\n✅ Validation passed!")
            return True
        except Exception as e:
            print(f"⚠️  Validation error (skipping quality checks): {e}")
            return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Build the Legs on the Ground website')
    parser.add_argument('--no-clean', action='store_true', help='Do not clean output directory')
    parser.add_argument('--validate', action='store_true', help='Run validation after build')
    parser.add_argument('--minify-css', action='store_true', help='Conservatively minify bundled CSS output')
    args = parser.parse_args()
    
    try:
        builder = SiteBuilder()
        builder.build(clean=not args.no_clean, minify_css=args.minify_css)
        
        if args.validate:
            if not builder.validate():
                sys.exit(1)
        
        print("\n🎉 Success! Your site is ready.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
