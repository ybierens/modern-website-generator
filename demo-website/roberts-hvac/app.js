import React from 'https://esm.sh/react@18.2.0';
import htm from 'https://esm.sh/htm@3.1.1';

// Initialize htm with React
const html = htm.bind(React.createElement);

// ============================================
// APP ROOT COMPONENT
// ============================================
export function App({ data }) {
  const [theme, setTheme] = React.useState('light');
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  React.useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const closeMobileMenu = () => setMobileMenuOpen(false);

  return html`
    <${React.Fragment}>
      <${TopBar} data=${data} theme=${theme} toggleTheme=${toggleTheme} />
      <${Nav} 
        data=${data} 
        mobileMenuOpen=${mobileMenuOpen}
        setMobileMenuOpen=${setMobileMenuOpen}
        closeMobileMenu=${closeMobileMenu}
      />
      <main id="main">
        <${Hero} data=${data} />
        <${Services} data=${data} />
        <${Story} data=${data} />
        <${Expertise} data=${data} />
        <${About} data=${data} />
        <${Team} data=${data} />
        <${Financing} data=${data} />
        <${Reviews} data=${data} />
        <${Maintenance} data=${data} />
        <${Contact} data=${data} />
        <${CTABand} data=${data} />
      </main>
      <${Footer} data=${data} />
      <${StickyCTA} data=${data} />
      <${SchemaMarkup} data=${data} />
    <//>
  `;
}

// ============================================
// TOP BAR COMPONENT
// ============================================
function TopBar({ data, theme, toggleTheme }) {
  return html`
    <div style=${{
      background: '#1e3a5f',
      color: 'white',
      padding: '8px 0',
      fontSize: '14px'
    }}>
      <div class="container" style=${{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <!-- Left: Rating -->
        <div style=${{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span style=${{ color: '#fbbf24', fontSize: '16px' }}>★★★★★</span>
          <span style=${{ fontSize: '13px' }}>
            Rated: <strong>5.0 / 5</strong> based on <strong>100+</strong> reviews. 
            <a href="#reviews" style=${{
              color: 'white',
              textDecoration: 'underline',
              marginLeft: '4px'
            }}>Read our reviews</a>
          </span>
          </div>

        <!-- Right: Phone -->
        <div style=${{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <span>📞</span>
          <span>We're available! Call <a href="tel:${data.company.phones[0]}" style=${{
            color: 'white',
            fontWeight: '700',
            textDecoration: 'underline'
          }}>${data.company.phones[0]}</a> to schedule your service</span>
        </div>
      </div>
    </div>
  `;
}

// ============================================
// NAVIGATION COMPONENT
// ============================================
function Nav({ data, mobileMenuOpen, setMobileMenuOpen, closeMobileMenu }) {
  const scrollToSection = (e, sectionId) => {
    e.preventDefault();
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
      closeMobileMenu();
    }
  };

  return html`
    <nav style=${{
      position: 'sticky',
      top: '0',
      background: 'white',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      zIndex: '1000',
      padding: '16px 0'
    }} aria-label="Primary">
      <div class="container">
        <div style=${{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '32px'
        }}>
          <!-- Logo -->
          <a href="#home" onClick=${(e) => scrollToSection(e, 'home')} style=${{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            textDecoration: 'none',
            color: '#1e3a5f',
            fontWeight: '700',
            fontSize: '18px'
          }}>
            <div style=${{ fontSize: '48px' }}>🏠</div>
            <span style=${{ whiteSpace: 'nowrap' }}>${data.company.name}</span>
          </a>
          
          <!-- Desktop Navigation -->
          <ul style=${{
            display: 'none',
            listStyle: 'none',
            margin: '0',
            padding: '0',
            gap: '32px',
            alignItems: 'center'
          }} class="desktop-nav">
            ${data.nav.map(item => html`
              <li key=${item}>
                <a 
                  href="#${item.toLowerCase()}"
                  onClick=${(e) => scrollToSection(e, item.toLowerCase())}
                  style=${{
                    color: '#1e3a5f',
                    textDecoration: 'none',
                    fontWeight: '600',
                    fontSize: '14px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                    whiteSpace: 'nowrap',
                    transition: 'color 0.3s ease'
                  }}
                  class="nav-link"
                >
                  ${item} ▾
                </a>
              </li>
            `)}
          </ul>

          <!-- CTA Button -->
          <a
            href="#contact"
            onClick=${(e) => scrollToSection(e, 'contact')}
            style=${{
              display: 'none',
              padding: '12px 32px',
              background: '#0ea5e9',
              color: 'white',
              fontSize: '14px',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              borderRadius: '4px',
              textDecoration: 'none',
              whiteSpace: 'nowrap',
              transition: 'all 0.3s ease'
            }}
            class="nav-cta-btn desktop-nav"
          >
            Schedule Service
          </a>

          <!-- Mobile Toggle -->
          <button 
            style=${{
              background: 'transparent',
              border: 'none',
              fontSize: '28px',
              color: '#1e3a5f',
              cursor: 'pointer',
              padding: '8px'
            }}
            class="mobile-toggle"
            onClick=${() => setMobileMenuOpen(true)}
            aria-label="Open menu"
            aria-expanded=${mobileMenuOpen}
          >
            ☰
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div 
        class="mobile-menu-overlay ${mobileMenuOpen ? 'open' : ''}"
        onClick=${closeMobileMenu}
      />
      <div class="mobile-menu ${mobileMenuOpen ? 'open' : ''}">
        <button 
          class="mobile-menu-close"
          onClick=${closeMobileMenu}
          aria-label="Close menu"
        >
          ✕
        </button>
        <ul class="mobile-menu-links">
          ${data.nav.map(item => html`
            <li key=${item}>
              <a 
                href="#${item.toLowerCase()}"
                onClick=${(e) => scrollToSection(e, item.toLowerCase())}
              >
                ${item}
              </a>
            </li>
          `)}
          <li>
            <a 
              href="#contact"
              onClick=${(e) => scrollToSection(e, 'contact')}
              style=${{ background: '#0ea5e9', color: 'white', borderRadius: '4px', padding: '12px', textAlign: 'center' }}
            >
              Schedule Service
            </a>
          </li>
        </ul>
      </div>
    </nav>
  `;
}

// ============================================
// HERO COMPONENT
// ============================================
function Hero({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section class="hero" id="home">
      <div class="hero-content">
        <h1>${data.hero.headline}</h1>
        <p>${data.hero.subheadline}</p>
        <div class="hero-ctas">
          <a href="#contact" class="btn btn-primary" onClick=${scrollToContact}>
            ${data.hero.primaryCta}
          </a>
          <a href="tel:${data.company.phones[0]}" class="btn btn-secondary">
            ${data.hero.secondaryCta}
          </a>
        </div>
      </div>
    </section>
  `;
}

// ============================================
// TRUST BAR COMPONENT
// ============================================
function TrustBar({ data }) {
  const icons = ['✓', '🔧', '🛡️', '💰', '🏆'];
  
  return html`
    <div class="trust-bar">
      <div class="container">
        <div class="trust-items">
          ${data.company.sellingPoints.map((point, idx) => html`
            <div key=${idx} class="trust-item">
              <div class="trust-item-icon">${icons[idx]}</div>
              <div class="trust-item-text">${point}</div>
            </div>
          `)}
        </div>
      </div>
    </div>
  `;
}

// ============================================
// SERVICES COMPONENT
// ============================================
function Services({ data }) {
  // Icon mapping for services
  const serviceIcons = {
    'Heating': '🔥',
    'Cooling': '❄️',
    'Indoor Air Quality': '💨',
    'Ductless Systems': '🏠',
    'Preventative Maintenance': '🔧'
  };

  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section id="services" style=${{ background: 'var(--bg)', padding: '64px 0' }}>
      <div class="container">
        <h2 style=${{ textAlign: 'center', marginBottom: '48px', fontSize: 'clamp(32px, 4vw, 48px)' }}>Our Services</h2>
        <div style=${{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '24px',
          marginBottom: '48px'
        }}>
          ${data.services.map((service, idx) => html`
            <div 
              key=${idx} 
              class="service-card-modern"
              style=${{
                background: 'var(--card)',
                border: '3px solid var(--text)',
                borderRadius: '16px',
                padding: '32px 24px',
                textAlign: 'center',
                transition: 'all 0.3s ease',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px'
              }}
            >
              <div style=${{
                fontSize: '48px',
                marginBottom: '8px'
              }}>
                ${serviceIcons[service.title] || '⚙️'}
                </div>
              <h3 style=${{
                fontSize: '20px',
                fontWeight: '700',
                color: 'var(--text)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                ${service.title}
              </h3>
              <p style=${{
                fontSize: '15px',
                color: 'var(--muted)',
                lineHeight: '1.5',
                flexGrow: '1'
              }}>
                ${service.desc}
              </p>
              <a 
                href="#contact"
                onClick=${scrollToContact}
                style=${{
                  color: 'var(--brand)',
                  fontWeight: '600',
                  fontSize: '14px',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  textDecoration: 'none',
                  marginTop: 'auto'
                }}
              >
                READ MORE →
              </a>
            </div>
          `)}
        </div>
        ${data.warranty && html`
          <div style=${{ textAlign: 'center', marginTop: '32px' }}>
            <span class="badge" style=${{
              fontSize: '16px',
              padding: '12px 24px',
              background: 'var(--brand)',
              color: 'white'
            }}>
              ${data.warranty}
            </span>
          </div>
        `}
      </div>
    </section>
  `;
}

// ============================================
// STORY COMPONENT
// ============================================
function Story({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section id="story" style=${{
      position: 'relative',
      padding: '60px 20px',
      background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
      color: 'white',
      overflow: 'hidden'
    }}>
      <!-- Background Pattern/Image Overlay -->
      <div style=${{
        position: 'absolute',
        top: '0',
        left: '0',
        right: '0',
        bottom: '0',
        backgroundImage: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
        opacity: '0.3',
        zIndex: '0'
      }}></div>

      <div class="container" style=${{
        maxWidth: '1200px',
        position: 'relative',
        zIndex: '1',
        textAlign: 'center'
      }}>
        <!-- Main Heading -->
        <h2 style=${{
          fontSize: 'clamp(28px, 4.5vw, 48px)',
          fontWeight: '700',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          marginBottom: '16px',
          lineHeight: '1.1'
        }}>
          The #1 Heating & Air Conditioning Company
          <br />
          in <span style=${{ color: '#fbbf24' }}>Versailles, KY</span>
        </h2>

        <!-- Accent Line -->
        <div style=${{
          width: '120px',
          height: '4px',
          background: '#fbbf24',
          margin: '0 auto 32px'
        }}></div>

        <!-- Story Content -->
        <div style=${{
          fontSize: 'clamp(15px, 1.8vw, 18px)',
          lineHeight: '1.6',
          maxWidth: '900px',
          margin: '0 auto'
        }}>
          <p style=${{ marginBottom: '16px' }}>
            ${data.company.name} is committed to offering <span style=${{ color: '#fbbf24', fontWeight: '600' }}>heating</span>, <span style=${{ color: '#fbbf24', fontWeight: '600' }}>air conditioning</span>, and <span style=${{ color: '#fbbf24', fontWeight: '600' }}>HVAC services</span> throughout ${data.company.serviceAreas.slice(0, 3).join(', ')}, and surrounding areas.
          </p>

          <p style=${{ marginBottom: '16px' }}>
            ${data.company.foundedCopy} We treat everyone like family and want our customers to have a great experience when choosing our team!
          </p>

          <p style=${{
            marginBottom: '28px',
            fontWeight: '700',
            fontSize: 'clamp(16px, 2vw, 19px)'
          }}>
            We use high-quality parts and materials for all aspects of our HVAC work, and will always ensure you're totally satisfied with our results.
          </p>

          <!-- CTA Button -->
          <a
            href="#contact"
            onClick=${scrollToContact}
            style=${{
              display: 'inline-block',
              padding: '18px 48px',
              background: 'white',
              color: '#0ea5e9',
              fontSize: '18px',
              fontWeight: '700',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              borderRadius: '8px',
              textDecoration: 'none',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(255, 255, 255, 0.3)'
            }}
            class="story-cta-btn"
          >
            Schedule Service
          </a>
        </div>
      </div>
    </section>
  `;
}

// ============================================
// EXPERTISE COMPONENT
// ============================================
function Expertise({ data }) {
  if (!data.expertise || data.expertise.length === 0) return null;

  const scrollToContact = (e, service) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section id="expertise" style=${{
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
      padding: '80px 0',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div class="container">
        <h2 style=${{
          textAlign: 'center',
          fontSize: 'clamp(28px, 5vw, 42px)',
          fontWeight: '700',
          color: '#1e293b',
          marginBottom: '16px',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          We're Highly Experienced With:
          <div style=${{
            width: '120px',
            height: '4px',
            background: '#0ea5e9',
            margin: '16px auto 0',
            borderRadius: '2px'
          }}></div>
        </h2>

        <div style=${{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginTop: '48px',
          maxWidth: '1400px',
          margin: '48px auto 0'
        }}>
          ${data.expertise.map((item, idx) => {
            return html`
              <a
                key=${idx}
                href="#contact"
                onClick=${(e) => scrollToContact(e, item)}
                style=${{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '20px 24px',
                  background: 'white',
                  border: '3px solid #0ea5e9',
                  borderRadius: '50px',
                  color: '#0ea5e9',
                  textDecoration: 'none',
                  fontWeight: '700',
                  fontSize: '16px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                class="expertise-pill"
              >
                <span>${item}</span>
                <span style=${{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '36px',
                  height: '36px',
                  border: '2px solid #0ea5e9',
                  borderRadius: '50%',
                  fontSize: '20px'
                }}>
                  →
                </span>
              </a>
            `;
          })}
        </div>
      </div>
    </section>
  `;
}

// ============================================
// ABOUT COMPONENT
// ============================================
function About({ data }) {
  return html`
    <section id="about">
      <div class="container">
        <h2 style=${{ textAlign: 'center' }}>About Us</h2>
        <div class="grid grid-2">
          <!-- Our Story Card -->
          <div class="card" style=${{
            padding: '48px 40px',
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            borderRadius: '12px',
            boxShadow: '0 8px 24px rgba(14, 165, 233, 0.25)',
            border: 'none',
            transition: 'all 0.3s ease'
          }}>
            <h3 style=${{
              color: 'white',
              fontSize: 'clamp(24px, 3vw, 32px)',
              fontWeight: '700',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              lineHeight: '1.2',
              textAlign: 'center'
            }}>
              Our Story
            </h3>
            
            <!-- Yellow Accent Line -->
            <div style=${{
              width: '80px',
              height: '4px',
              background: '#fbbf24',
              margin: '0 auto 32px',
              borderRadius: '2px'
            }}></div>
            
            <p style=${{
              lineHeight: '1.8',
              color: 'white',
              fontSize: '16px',
              marginBottom: '24px'
            }}>${data.company.foundedCopy}</p>
            
            <p style=${{
              lineHeight: '1.8',
              color: 'white',
              fontSize: '16px',
              marginBottom: '32px'
            }}>
              <strong style=${{ color: '#fbbf24' }}>License:</strong> ${data.company.license}
            </p>
            
            <div style=${{ textAlign: 'center' }}>
              <a
                href="#contact"
                onClick=${(e) => {
                  e.preventDefault();
                  document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
                }}
                style=${{
                  display: 'inline-block',
                  padding: '14px 32px',
                  background: 'white',
                  color: '#0ea5e9',
                  fontSize: '16px',
                  fontWeight: '700',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  transition: 'all 0.3s ease'
                }}
              >
                Schedule Service
              </a>
            </div>
          </div>

          <!-- Service Areas Card -->
          <div class="card" style=${{
            padding: '48px 40px',
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            borderRadius: '12px',
            boxShadow: '0 8px 24px rgba(14, 165, 233, 0.25)',
            border: 'none',
            transition: 'all 0.3s ease'
          }}>
            <h3 style=${{
              color: 'white',
              fontSize: 'clamp(24px, 3vw, 32px)',
              fontWeight: '700',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              lineHeight: '1.2',
              textAlign: 'center'
            }}>
              Service Areas
            </h3>
            
            <!-- Yellow Accent Line -->
            <div style=${{
              width: '80px',
              height: '4px',
              background: '#fbbf24',
              margin: '0 auto 32px',
              borderRadius: '2px'
            }}></div>
            
            <p style=${{
              lineHeight: '1.8',
              color: 'white',
              fontSize: '16px',
              marginBottom: '24px',
              textAlign: 'center'
            }}>We proudly serve:</p>
            
            <div style=${{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '12px',
              marginBottom: '32px',
              justifyContent: 'center'
            }}>
              ${data.company.serviceAreas.map((area, idx) => html`
                <span key=${idx} style=${{
                  padding: '10px 20px',
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: '6px',
                  color: 'white',
                  fontWeight: '600',
                  fontSize: '15px',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}>
                  ${area}
                </span>
              `)}
            </div>
            
            <div style=${{ textAlign: 'center' }}>
              <a
                href="#contact"
                onClick=${(e) => {
                  e.preventDefault();
                  document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
                }}
                style=${{
                  display: 'inline-block',
                  padding: '14px 32px',
                  background: 'white',
                  color: '#0ea5e9',
                  fontSize: '16px',
                  fontWeight: '700',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  transition: 'all 0.3s ease'
                }}
              >
                Contact Us
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  `;
}

// ============================================
// TEAM COMPONENT
// ============================================
function Team({ data }) {
  if (!data.team || data.team.length === 0) return null;

  return html`
    <section id="team" style=${{
      background: '#f5f5f5',
      padding: '80px 20px'
    }}>
      <div class="container">
        <h2 style=${{
          textAlign: 'center',
          fontSize: 'clamp(32px, 4vw, 48px)',
          fontWeight: '700',
          color: '#1e3a5f',
          marginBottom: '64px'
        }}>Meet Our Team</h2>

        <div style=${{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '48px',
          maxWidth: '1200px',
          margin: '0 auto'
        }}>
          ${data.team.map((member, idx) => html`
            <div key=${idx} style=${{
              textAlign: 'center',
              position: 'relative'
            }}>
              <!-- Decorative Arch Frame -->
              <div style=${{
                position: 'relative',
                marginBottom: '32px'
              }}>
                <!-- Arch Shape Container -->
                <div style=${{
                  position: 'relative',
                  width: '100%',
                  paddingTop: '100%',
                  background: 'white',
                  border: '4px solid #1e3a5f',
                  borderRadius: '50% 50% 0 0',
                  overflow: 'hidden',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.1)',
                  display: 'flex',
                  alignItems: 'flex-end',
                  justifyContent: 'center'
                }}>
                  <!-- Decorative Leaves at Top -->
                  <div style=${{
                    position: 'absolute',
                    top: '0',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    gap: '8px',
                    zIndex: '2'
                  }}>
                    <!-- Left Leaves -->
                    <div style=${{
                      width: '60px',
                      height: '80px',
                      background: '#b8dfd8',
                      border: '2px solid #1e3a5f',
                      borderRadius: '50% 0 50% 0',
                      transform: 'rotate(-20deg)'
                    }}></div>
                    <div style=${{
                      width: '50px',
                      height: '70px',
                      background: '#b8dfd8',
                      border: '2px solid #1e3a5f',
                      borderRadius: '50% 0 50% 0',
                      transform: 'rotate(-10deg)',
                      marginTop: '10px'
                    }}></div>
                    
                    <!-- Center Leaf -->
                    <div style=${{
                      width: '55px',
                      height: '75px',
                      background: '#a8d5cc',
                      border: '2px solid #1e3a5f',
                      borderRadius: '50% 50% 50% 50%',
                      marginTop: '5px'
                    }}></div>
                    
                    <!-- Right Leaves -->
                    <div style=${{
                      width: '50px',
                      height: '70px',
                      background: '#b8dfd8',
                      border: '2px solid #1e3a5f',
                      borderRadius: '0 50% 0 50%',
                      transform: 'rotate(10deg)',
                      marginTop: '10px'
                    }}></div>
                    <div style=${{
                      width: '60px',
                      height: '80px',
                      background: '#b8dfd8',
                      border: '2px solid #1e3a5f',
                      borderRadius: '0 50% 0 50%',
                      transform: 'rotate(20deg)'
                    }}></div>
                  </div>

                  <!-- Icon/Avatar -->
                  <div style=${{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    fontSize: '120px',
                    zIndex: '1'
                  }}>
                    ${member.icon}
                  </div>
                </div>
              </div>

              <!-- Name -->
              <h3 style=${{
                fontSize: '26px',
                fontWeight: '700',
                color: '#1e3a5f',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                marginBottom: '8px'
              }}>
                ${member.name}
              </h3>

              <!-- Title -->
              <p style=${{
                fontSize: '20px',
                fontWeight: '600',
                color: '#0ea5e9',
                letterSpacing: '0.5px'
              }}>
                ${member.title}
              </p>
            </div>
          `)}
        </div>
      </div>
    </section>
  `;
}

// ============================================
// FINANCING COMPONENT
// ============================================
function Financing({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section id="financing">
      <div class="container">
        <h2 style=${{ textAlign: 'center' }}>${data.financing.headline}</h2>
        <div class="grid grid-2">
          ${data.financing.items.map((item, idx) => html`
            <div key=${idx} class="card" style=${{ textAlign: 'center' }}>
              <h3>${item}</h3>
              <p style=${{ color: 'var(--muted)' }}>
                ${idx === 0 ? 'Secure online payment options available for your convenience.' : 'Flexible financing options to fit your budget. Ask us for details.'}
              </p>
              <button class="btn btn-primary" style=${{ marginTop: '16px' }} onClick=${scrollToContact}>
                Learn More
              </button>
            </div>
          `)}
        </div>
      </div>
    </section>
  `;
}

// ============================================
// MAINTENANCE PROGRAM COMPONENT
// ============================================
function Maintenance({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section id="maintenance">
      <div class="container">
        <h2 style=${{ textAlign: 'center' }}>${data.maintenanceProgram.headline}</h2>
        <div class="card" style=${{
          maxWidth: '800px',
          margin: '0 auto',
          padding: '48px 40px',
          background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(14, 165, 233, 0.25)',
          border: 'none',
          transition: 'all 0.3s ease'
        }}>
          <h3 style=${{
            color: 'white',
            fontSize: 'clamp(24px, 3vw, 32px)',
            fontWeight: '700',
            marginBottom: '16px',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            lineHeight: '1.2',
            textAlign: 'center'
          }}>
            Benefits
          </h3>
          
          <!-- Yellow Accent Line -->
          <div style=${{
            width: '80px',
            height: '4px',
            background: '#fbbf24',
            margin: '0 auto 32px',
            borderRadius: '2px'
          }}></div>
          
          <ul style=${{ 
            listStyle: 'none', 
            padding: '0', 
            marginBottom: '32px', 
            textAlign: 'center' 
          }}>
            ${data.maintenanceProgram.bullets.map((bullet, idx) => html`
              <li key=${idx} style=${{
                marginBottom: '16px',
                color: 'white',
                fontSize: '16px',
                lineHeight: '1.8'
              }}>${bullet}</li>
            `)}
          </ul>
          
          <div style=${{ textAlign: 'center' }}>
            <button 
              class="btn btn-primary" 
              onClick=${scrollToContact}
              style=${{
                padding: '14px 32px',
                background: 'white',
                color: '#0ea5e9',
                fontSize: '16px',
                fontWeight: '700',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
            >
              ${data.maintenanceProgram.cta}
            </button>
          </div>
        </div>
      </div>
    </section>
  `;
}

// ============================================
// REVIEWS COMPONENT
// ============================================
function Reviews({ data }) {
  if (!data.reviews || data.reviews.length === 0) return null;

  const [currentReview, setCurrentReview] = React.useState(0);
  const review = data.reviews[currentReview];

  // Auto-rotate reviews every 8 seconds
  React.useEffect(() => {
    const interval = setInterval(() => {
      setCurrentReview((prev) => (prev + 1) % data.reviews.length);
    }, 8000);
    return () => clearInterval(interval);
  }, [data.reviews.length]);

  return html`
    <section id="reviews" style=${{
      background: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
      padding: '80px 20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <!-- Decorative chevron shapes -->
      <div style=${{
        position: 'absolute',
        left: '0',
        top: '0',
        bottom: '0',
        width: '80px',
        background: '#1e293b',
        clipPath: 'polygon(0 0, 100% 50%, 0 100%)'
      }}></div>
      <div style=${{
        position: 'absolute',
        right: '0',
        top: '0',
        bottom: '0',
        width: '80px',
        background: '#1e293b',
        clipPath: 'polygon(100% 0, 0 50%, 100% 100%)'
      }}></div>

      <div class="container" style=${{
        maxWidth: '900px',
        textAlign: 'center',
        position: 'relative',
        zIndex: '1'
      }}>
        <!-- Star Rating -->
        <div style=${{
          fontSize: '48px',
          marginBottom: '32px',
          color: 'white'
        }}>
          ${'★'.repeat(review.rating)}
              </div>

        <!-- Review Text -->
        <blockquote style=${{
          fontSize: 'clamp(20px, 3vw, 28px)',
          lineHeight: '1.6',
          color: 'white',
          fontWeight: '600',
          marginBottom: '32px',
          fontStyle: 'normal',
          padding: '0 20px'
        }}>
          "${review.text}"
        </blockquote>

        <!-- Author -->
        <p style=${{
          fontSize: '20px',
          color: 'white',
          fontWeight: '700',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          -${review.name}
        </p>

        <!-- Navigation Dots -->
        ${data.reviews.length > 1 && html`
          <div style=${{
            display: 'flex',
            gap: '12px',
            justifyContent: 'center',
            marginTop: '40px'
          }}>
            ${data.reviews.map((_, idx) => html`
              <button
                key=${idx}
                onClick=${() => setCurrentReview(idx)}
                style=${{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  border: 'none',
                  background: idx === currentReview ? 'white' : 'rgba(255, 255, 255, 0.4)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                aria-label="View review ${idx + 1}"
              />
            `)}
            </div>
        `}
      </div>
    </section>
  `;
}

// ============================================
// CTA BAND COMPONENT
// ============================================
function CTABand({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <section class="cta-band">
      <div class="container">
        <h2>Ready to Get Started?</h2>
        <div class="cta-band-content">
          <div class="cta-band-phones">
            ${data.company.phones.map(phone => html`
              <a key=${phone} href="tel:${phone}">${phone}</a>
            `)}
          </div>
          <button class="btn btn-primary" onClick=${scrollToContact} style=${{ background: 'white', color: 'var(--brand)' }}>
            ${data.hero.primaryCta}
          </button>
        </div>
      </div>
    </section>
  `;
}

// ============================================
// CONTACT COMPONENT
// ============================================
function Contact({ data }) {
  const [formData, setFormData] = React.useState({
    name: '',
    phone: '',
    email: '',
    address: '',
    serviceType: '',
    message: ''
  });
  const [formStatus, setFormStatus] = React.useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.phone || !formData.email) {
      setFormStatus({ type: 'error', message: 'Please fill in all required fields.' });
      return;
    }

    const phoneRegex = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
    if (!phoneRegex.test(formData.phone)) {
      setFormStatus({ type: 'error', message: 'Please enter a valid phone number.' });
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setFormStatus({ type: 'error', message: 'Please enter a valid email address.' });
      return;
    }

    const body = `
Name: ${formData.name}
Phone: ${formData.phone}
Email: ${formData.email}
Address: ${formData.address}
Service Type: ${formData.serviceType}
Message: ${formData.message}
    `.trim();

    const mailtoLink = `mailto:${data.company.emails[0]}?subject=New Contact Form Submission&body=${encodeURIComponent(body)}`;
    window.location.href = mailtoLink;

    setFormStatus({ type: 'success', message: 'Opening your email client...' });
    
    setTimeout(() => {
      setFormData({
        name: '',
        phone: '',
        email: '',
        address: '',
        serviceType: '',
        message: ''
      });
      setFormStatus(null);
    }, 3000);
  };

  return html`
    <section id="contact">
      <div class="container">
        <h2>${data.contact.headline}</h2>
        
        <div class="grid grid-2" style=${{ marginBottom: '48px' }}>
          <div class="card" style=${{
            padding: '48px 40px',
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            borderRadius: '12px',
            boxShadow: '0 8px 24px rgba(14, 165, 233, 0.25)',
            border: 'none',
            transition: 'all 0.3s ease'
          }}>
            <h3 style=${{
              color: 'white',
              fontSize: 'clamp(24px, 3vw, 32px)',
              fontWeight: '700',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              lineHeight: '1.2',
              textAlign: 'center'
            }}>
              Contact Information
            </h3>
            
            <!-- Yellow Accent Line -->
            <div style=${{
              width: '80px',
              height: '4px',
              background: '#fbbf24',
              margin: '0 auto 32px',
              borderRadius: '2px'
            }}></div>
            
            <p style=${{
              marginBottom: '20px',
              color: 'white',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              <strong style=${{ color: '#fbbf24' }}>Phone:</strong><br/>
              ${data.company.phones.map(phone => html`
                <span key=${phone}>
                  <a href="tel:${phone}" style=${{ color: 'white', textDecoration: 'underline' }}>${phone}</a><br/>
                </span>
              `)}
            </p>
            <p style=${{
              marginBottom: '20px',
              color: 'white',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              <strong style=${{ color: '#fbbf24' }}>Email:</strong><br/>
              ${data.company.emails.map(email => html`
                <span key=${email}>
                  <a href="mailto:${email}" style=${{ color: 'white', textDecoration: 'underline' }}>${email}</a><br/>
                </span>
              `)}
            </p>
            <p style=${{
              marginBottom: '20px',
              color: 'white',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              <strong style=${{ color: '#fbbf24' }}>Business Address:</strong><br/>
              ${data.company.addresses.business}
            </p>
            <p style=${{
              color: 'white',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              <strong style=${{ color: '#fbbf24' }}>Hours:</strong><br/>
              ${data.contact.hours}
            </p>
          </div>

          <div class="card" style=${{
            padding: '48px 40px',
            background: 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
            borderRadius: '12px',
            boxShadow: '0 8px 24px rgba(14, 165, 233, 0.25)',
            border: 'none',
            transition: 'all 0.3s ease'
          }}>
            <h3 style=${{
              color: 'white',
              fontSize: 'clamp(24px, 3vw, 32px)',
              fontWeight: '700',
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              lineHeight: '1.2',
              textAlign: 'center'
            }}>
              Notes
            </h3>
            
            <!-- Yellow Accent Line -->
            <div style=${{
              width: '80px',
              height: '4px',
              background: '#fbbf24',
              margin: '0 auto 32px',
              borderRadius: '2px'
            }}></div>
            
            <ul style=${{ 
              marginLeft: '0',
              padding: '0',
              listStyle: 'none'
            }}>
              ${data.contact.notes.map((note, idx) => html`
                <li key=${idx} style=${{
                  marginBottom: '16px',
                  color: 'white',
                  fontSize: '16px',
                  lineHeight: '1.8',
                  paddingLeft: '24px',
                  position: 'relative'
                }}>
                  <span style=${{
                    position: 'absolute',
                    left: '0',
                    color: '#fbbf24',
                    fontWeight: '700'
                  }}>•</span>
                  ${note}
                </li>
              `)}
            </ul>
          </div>
        </div>

        <form class="contact-form" onSubmit=${handleSubmit}>
          <h3 style=${{ textAlign: 'center', marginBottom: '24px' }}>Request a Free Estimate</h3>
          
          ${formStatus && html`
            <div class="form-message ${formStatus.type}">
              ${formStatus.message}
            </div>
          `}

          <div class="form-row">
            <div class="form-group">
              <label htmlFor="name">Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value=${formData.name}
                onInput=${handleChange}
                required
              />
            </div>
            <div class="form-group">
              <label htmlFor="phone">Phone *</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value=${formData.phone}
                onInput=${handleChange}
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value=${formData.email}
              onInput=${handleChange}
              required
            />
          </div>

          <div class="form-group">
            <label htmlFor="address">Address</label>
            <input
              type="text"
              id="address"
              name="address"
              value=${formData.address}
              onInput=${handleChange}
            />
          </div>

          <div class="form-group">
            <label htmlFor="serviceType">Service Type</label>
            <select
              id="serviceType"
              name="serviceType"
              value=${formData.serviceType}
              onInput=${handleChange}
            >
              <option value="">Select a service...</option>
              ${data.services.map((service, idx) => html`
                <option key=${idx} value=${service.title}>${service.title}</option>
              `)}
              <option value="maintenance">Maintenance Program</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label htmlFor="message">Message</label>
            <textarea
              id="message"
              name="message"
              value=${formData.message}
              onInput=${handleChange}
              rows="5"
            />
          </div>

          <button type="submit" class="btn btn-primary" style=${{ width: '100%' }}>
            Send Message
          </button>
        </form>
      </div>
    </section>
  `;
}

// ============================================
// FAQ COMPONENT
// ============================================
function FAQ({ data }) {
  return html`
    <section id="faq" style=${{ background: 'var(--card)' }}>
      <div class="container">
        <h2>Frequently Asked Questions</h2>
        <div style=${{ maxWidth: '800px', margin: '0 auto' }}>
          ${data.faqs.map((faq, idx) => html`
            <div key=${idx} class="faq-item">
              <h4>${faq.q}</h4>
              <p>${faq.a}</p>
            </div>
          `)}
        </div>
      </div>
    </section>
  `;
}

// ============================================
// FOOTER COMPONENT
// ============================================
function Footer({ data }) {
  const scrollToSection = (e, href) => {
    if (href.startsWith('#')) {
      e.preventDefault();
      const sectionId = href.substring(1);
      document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return html`
    <footer style=${{
      background: '#e0f2fe',
      padding: '60px 20px 40px',
      color: '#1e293b'
    }}>
      <div class="container" style=${{ maxWidth: '1400px' }}>
        <div style=${{
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          gap: '40px',
          alignItems: 'start',
          marginBottom: '40px'
        }} class="footer-grid">
          
          <!-- Contact Info Box -->
          <div style=${{
            background: 'white',
            border: '4px solid #0ea5e9',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.15)'
          }}>
            <h3 style=${{
              fontSize: '24px',
              fontWeight: '700',
              color: '#0ea5e9',
              textTransform: 'uppercase',
              marginBottom: '24px',
              letterSpacing: '1px'
            }}>Contact Info</h3>
            
            <div style=${{ marginBottom: '20px' }}>
              <h4 style=${{
                fontSize: '18px',
                fontWeight: '600',
                marginBottom: '12px',
                color: '#1e293b'
              }}>Office Address</h4>
              <p style=${{ marginBottom: '8px', color: '#475569' }}>${data.company.addresses.business}</p>
              <a href="#" style=${{
                color: '#0ea5e9',
                fontWeight: '600',
                textDecoration: 'none'
              }}>Map & Directions [+]</a>
          </div>

            <div style=${{ marginBottom: '20px' }}>
              <h4 style=${{
                fontSize: '18px',
                fontWeight: '600',
                marginBottom: '12px',
                color: '#1e293b'
              }}>Office Hours</h4>
              <p style=${{ color: '#475569' }}>${data.contact.hours}</p>
          </div>

            <div>
              <p style=${{ fontWeight: '700', color: '#0ea5e9' }}>*24/7 Emergency Service</p>
            </div>
          </div>

          <!-- Center: Logo, Phone, Social -->
          <div style=${{
            textAlign: 'center',
            minWidth: '300px'
          }}>
            <div style=${{
              fontSize: '48px',
              marginBottom: '16px'
            }}>🏠</div>
            <h2 style=${{
              fontSize: '20px',
              fontWeight: '700',
              color: '#1e293b',
              marginBottom: '16px'
            }}>${data.company.name}</h2>
            
            <a href="tel:${data.company.phones[0]}" style=${{
              fontSize: 'clamp(32px, 5vw, 48px)',
              fontWeight: '700',
              color: '#0ea5e9',
              textDecoration: 'none',
              display: 'block',
              marginBottom: '16px'
            }}>
              ${data.company.phones[0]}
            </a>

            <p style=${{
              fontSize: '16px',
              fontStyle: 'italic',
              color: '#475569',
              marginBottom: '24px'
            }}>
              ${data.company.tagline}
            </p>

            <!-- Social Media Icons -->
            <div style=${{
              display: 'flex',
              gap: '16px',
              justifyContent: 'center',
              fontSize: '32px'
            }}>
              <a href="#" aria-label="Facebook" style=${{ color: '#0ea5e9' }}>📘</a>
              <a href="#" aria-label="Instagram" style=${{ color: '#0ea5e9' }}>📷</a>
              <a href="#" aria-label="YouTube" style=${{ color: '#0ea5e9' }}>▶️</a>
              <a href="#" aria-label="LinkedIn" style=${{ color: '#0ea5e9' }}>💼</a>
              <a href="#" aria-label="TikTok" style=${{ color: '#0ea5e9' }}>🎵</a>
              </div>
            </div>

          <!-- Helpful Links Box -->
          <div style=${{
            background: 'white',
            border: '4px solid #0ea5e9',
            borderRadius: '16px',
            padding: '32px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.15)'
          }}>
            <h3 style=${{
              fontSize: '24px',
              fontWeight: '700',
              color: '#0ea5e9',
              textTransform: 'uppercase',
              marginBottom: '24px',
              letterSpacing: '1px'
            }}>Helpful Links</h3>
            
            <div style=${{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px'
            }}>
              ${data.helpfulLinks.map((link, idx) => {
                const isTeal = idx === 0;
                return html`
                  <a
                    key=${idx}
                    href=${link.href}
                    onClick=${(e) => scrollToSection(e, link.href)}
                    style=${{
                      display: 'block',
                      padding: '14px 24px',
                      background: isTeal ? '#0ea5e9' : '#1e293b',
                      color: 'white',
                      textAlign: 'center',
                      fontWeight: '700',
                      fontSize: '14px',
                      textTransform: 'uppercase',
                      letterSpacing: '1px',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      transition: 'all 0.3s ease'
                    }}
                    class="footer-link-btn"
                  >
                    ${link.text}
                  </a>
                `;
              })}
            </div>
          </div>
        </div>

        <!-- Bottom Copyright -->
        <div style=${{
          textAlign: 'center',
          paddingTop: '24px',
          borderTop: '2px solid rgba(14, 165, 233, 0.2)',
          fontSize: '14px',
          color: '#475569'
        }}>
          <p>${data.legal.copyright} | ${data.legal.license}</p>
        </div>
      </div>
    </footer>
  `;
}

// ============================================
// STICKY CTA COMPONENT (Mobile)
// ============================================
function StickyCTA({ data }) {
  const scrollToContact = (e) => {
    e.preventDefault();
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
  };

  return html`
    <div class="sticky-cta">
      <a href="tel:${data.company.phones[0]}" class="btn btn-primary">
        📞 Call Now
      </a>
      <button class="btn btn-secondary" onClick=${scrollToContact}>
        Free Estimate
      </button>
    </div>
  `;
}

// ============================================
// SCHEMA MARKUP COMPONENT (SEO)
// ============================================
function SchemaMarkup({ data }) {
  const schema = {
    "@context": "https://schema.org",
    "@type": "HVACBusiness",
    "name": data.company.name,
    "description": data.company.tagline,
    "telephone": data.company.phones,
    "email": data.company.emails[0],
    "address": {
      "@type": "PostalAddress",
      "streetAddress": data.company.addresses.business.split(',')[0],
      "addressLocality": "Versailles",
      "addressRegion": "KY",
      "postalCode": "40383",
      "addressCountry": "US"
    },
    "areaServed": data.company.serviceAreas.map(area => ({
      "@type": "City",
      "name": area
    })),
    "priceRange": "$$",
    "foundingDate": "1992"
  };

  return html`
    <script 
      type="application/ld+json"
      dangerouslySetInnerHTML=${{ __html: JSON.stringify(schema) }}
    />
  `;
}
