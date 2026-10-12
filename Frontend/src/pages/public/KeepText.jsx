import {Link} from 'react-router-dom';
import Logo from '../../components/common/Logo';
import Icon from '../../components/common/Icon';
import '../../components/layout/AppShell.css';


export default function LandingPage(){
    return (
        <div className="landing">

            <header className="landing-header">
                <Logo className="landing-logo"/>
                <div className="row">
                    <Link to="/login" className="btn btn-ghost">Log in</Link>
                    <Link to="/register" className="btn btn-primary">Create account</Link>
                </div>
            </header>

            <section className="landing-hero">
                <div>
                    <div className="eyebrow">Geology student learning platform</div>
                    <div className="hero-title">Learn deeply.<br/>
                        <span>Practice with purpose.</span>
                    </div>
                    <p className="hero-copy">PageTurners brings course materials, focused practice,
                         academic progress and healthy competition into one professional learning
                          workspace for Geology students.
                    </p>
                    <div className="row" style={{marginTop:26}}>
                        <Link to="/register" className="btn btn-primary">
                            Start learning 
                            <Icon name="arrow"/>
                        </Link>
                        <Link to="/login" className="btn btn-secondary">
                            Explore the workspace
                        </Link>
                    </div>
                </div>
                <div className="hero-panel">
                    <div className="hero-book">
                        <div className="row space-between">
                            <div>
                                <div className="eyebrow">Today</div>
                                <h3 style={{marginTop:8}}>AGP 301 · Geophysical Methods</h3>
                            </div>
                            <span className="badge">72% complete</span>
                        </div>
                        <div className="progress-track" style={{margin:'18px 0'}}>
                            <div className="progress-value" style={{width:'72%'}}/>
                        </div>
                        <div className="grid-2">
                            <div className="notice">
                                <strong>8 day streak</strong>
                                <div className="muted" style={{fontSize:12}}>Keep your momentum.</div>
                            </div>
                            <div className="notice">
                                <strong>+80 points</strong>
                                <div className="muted" style={{fontSize:12}}>This week's progress.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <section className="landing-section alt">
                <div>
                    <div className="eyebrow">Built around study</div>
                    <h2>Everything you need to keep moving.</h2>
                    <div className="grid-3" style={{marginTop:26}}>
                        {
                            [
                                ['book','Course learning','Organized courses, topics and readable lesson notes.'],
                                ['target','Practice questions','Immediate feedback, explanations and measurable progress.'],
                                ['chart','Progress & community','Track performance and participate in academic leaderboards.']
                            ].map(
                                    ([icon,title,text])=>
                                        <div className="card feature-card" key={title}>
                                            <span style={{color:'var(--color-primary)'}}>
                                                <Icon name={icon} size={24}/>
                                            </span>
                                            <h3 style={{marginTop:18}}>{title}</h3>
                                            <p className="muted" style={{marginBottom:0}}>{text}</p>
                                        </div>
                                )
                        }
                    </div>
                </div>
            </section>
            
            <section className="landing-section">
                <div className="grid-2">
                    <div>
                    <div className="eyebrow">Academic progression</div>
                    <h2>Separate your university level from your learning level.</h2>
                    <p className="muted">A 300 Level student can be a Beginner, 
                        Scholar or Expert based on learning activity. 
                        The two concepts remain distinct throughout the product.
                    </p>
                </div>
                <div className="card card-pad">
                    <div className="row space-between">
                        <span>Learning progression</span>
                        <strong>Level 4 · Scholar</strong>
                    </div>
                    {
                        [
                            'Beginner',
                            'Explorer',
                            'Learner',
                            'Scholar',
                            'Advanced Scholar',
                            'Expert',
                            'Master'
                        ].map(
                            (x,i)=>
                            <div key={x} 
                                style={
                                        {
                                            display:'flex',
                                            alignItems:'center',
                                            gap:12,padding:'11px 0',
                                            borderBottom:i<6?'1px solid var(--color-border)':'none'
                                        }
                                    }>
                                        <span className="badge">{i+1}</span>
                                        <span>{x}</span>
                                        {i===3&&<span className="badge badge-success" style={{marginLeft:'auto'}}>Current</span>}</div>
                            )
                    }
                    </div>
                </div>
            </section>
        
            <section className="landing-section alt">
                <div className="row space-between" style={{flexWrap:'wrap'}}>
                    <div>
                        <div className="eyebrow">Ready when you are</div>
                        <h2>Turn your next study session into progress.</h2>
                    </div>
                    <Link to="/register" className="btn btn-primary">
                        Create your account 
                        <Icon name="arrow"/>
                    </Link>
                </div>
            </section>
        
            <footer className="footer">
                <div style={{maxWidth:1280,margin:'0 auto'}}>© 2026 PageTurners · Geology education platform</div>
            </footer>
        </div>
    );
}
