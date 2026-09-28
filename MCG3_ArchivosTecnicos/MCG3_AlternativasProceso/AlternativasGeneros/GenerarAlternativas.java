import javax.sound.midi.*;
import javax.sound.sampled.*;
import com.sun.media.sound.AudioSynthesizer;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Arreglos reproducibles a partir de los MIDI originales. Java 11+. */
public class GenerarAlternativas {
 // Evitar preferencias del registro: el render no necesita configuracion global.
 public static class MemoryPreferences extends java.util.prefs.AbstractPreferences {
  Map<String,String> values=new HashMap<>();
  MemoryPreferences(java.util.prefs.AbstractPreferences p,String n){super(p,n);}
  protected void putSpi(String k,String v){values.put(k,v);} protected String getSpi(String k){return values.get(k);}
  protected void removeSpi(String k){values.remove(k);} protected void removeNodeSpi(){} protected String[] keysSpi(){return values.keySet().toArray(new String[0]);}
  protected String[] childrenNamesSpi(){return new String[0];} protected java.util.prefs.AbstractPreferences childSpi(String n){return new MemoryPreferences(this,n);}
  protected void syncSpi(){} protected void flushSpi(){}
 }
 public static class MemoryFactory implements java.util.prefs.PreferencesFactory {
  final java.util.prefs.Preferences root=new MemoryPreferences(null,"");
  public java.util.prefs.Preferences userRoot(){return root;} public java.util.prefs.Preferences systemRoot(){return root;}
 }
 static final Path OUT=Paths.get("AlternativasGeneros");
 static final double BPM=124, SEC=60/BPM;
 static final int SR=22050;
 static class Variante {
  String nombre,fuente; int tipo,drop,solo,retorno; double wet; int seed;
  Variante(String n,String f,int t,int d,int s,int r,double w,int seed){nombre=n;fuente=f;tipo=t;drop=d;solo=s;retorno=r;wet=w;this.seed=seed;}
 }
 static Variante[] variantes={
  new Variante("01_Salsa_Patio","Salsa",0,228,230,238,.48,101),
  new Variante("02_Salsa_Horizonte","Salsa",1,228,232,244,.66,202),
  new Variante("03_Funk_Brasileno_Aire","Brazilian_Funk",2,228,230,238,.43,303),
  new Variante("04_Funk_Brasileno_Eco","Brazilian_Funk",3,228,232,244,.62,404),
  new Variante("05_Reggaeton_Abierto","Reggaeton",4,228,232,240,.57,505)
 };
 static void msg(Track t,int command,int ch,int a,int b,long tick)throws Exception{ShortMessage m=new ShortMessage();m.setMessage(command,ch,a,b);t.add(new MidiEvent(m,tick));}
 static void meta(Track t,int type,String text,long tick)throws Exception{MetaMessage m=new MetaMessage();m.setMessage(type,text.getBytes(StandardCharsets.UTF_8),text.getBytes(StandardCharsets.UTF_8).length);t.add(new MidiEvent(m,tick));}
 static void note(Track t,int ch,int pitch,int vel,double beat,double len,int ppq)throws Exception{msg(t,144,ch,pitch,Math.max(1,Math.min(127,vel)),Math.round(beat*ppq));msg(t,128,ch,pitch,0,Math.round((beat+len)*ppq));}
 static double gain(double b,Variante v){if(b>=v.drop&&b<v.retorno)return 0;if(b>=v.drop-12&&b<v.drop)return 1-.78*(b-(v.drop-12))/12;return b>=v.retorno?1.13:1;}
 static boolean active(double b,Variante v){return !(b>=v.drop&&b<v.retorno);}
 static Sequence arrange(Variante v)throws Exception{
  Sequence src=MidiSystem.getSequence(Paths.get("Grupo3_EX3_Piano_Generativo_"+v.fuente+".mid").toFile());int ppq=src.getResolution();Sequence dst=new Sequence(Sequence.PPQ,ppq);
  Track conductor=dst.createTrack();for(int i=0;i<src.getTracks()[0].size();i++){MidiEvent e=src.getTracks()[0].get(i);if(!(e.getMessage() instanceof MetaMessage)||((MetaMessage)e.getMessage()).getType()!=47)conductor.add(new MidiEvent((MidiMessage)e.getMessage().clone(),e.getTick()));}
  meta(conductor,3,v.nombre,0);
  meta(conductor,6,"Bajada progresiva",(v.drop-12)*ppq);meta(conductor,6,"DROP: corte del conjunto",v.drop*ppq);meta(conductor,6,"Piano solo",v.solo*ppq);meta(conductor,6,"Regreso con toda la energia",v.retorno*ppq);
  for(int ti=1;ti<src.getTracks().length;ti++){
   Track input=src.getTracks()[ti],output=dst.createTrack();
   for(int i=0;i<input.size();i++){
    MidiEvent e=input.get(i);MidiMessage raw=e.getMessage();double b=e.getTick()/(double)ppq;
    if(raw instanceof MetaMessage){if(((MetaMessage)raw).getType()!=47)output.add(new MidiEvent((MidiMessage)raw.clone(),e.getTick()));continue;}
    if(!(raw instanceof ShortMessage))continue;ShortMessage m=(ShortMessage)raw;int ch=m.getChannel(),p=m.getData1();
    if(m.getCommand()==128||(m.getCommand()==144&&m.getData2()==0))continue;
    if(m.getCommand()!=144){output.add(new MidiEvent((MidiMessage)m.clone(),e.getTick()));continue;}
    // Sustituir el pulso house por patrones propios de cada alternativa.
    if(ch==9&&(p==36||p==35||p==38||p==40||p==42||p==44||p==46||p==70||p==82))continue;
    if(b>=v.drop&&b<v.retorno&&(ch!=2||b<v.solo))continue;
    long end=e.getTick()+ppq/4;
    for(int j=i+1;j<input.size();j++){MidiEvent z=input.get(j);if(z.getMessage() instanceof ShortMessage){ShortMessage q=(ShortMessage)z.getMessage();if(q.getChannel()==ch&&q.getData1()==p&&(q.getCommand()==128||(q.getCommand()==144&&q.getData2()==0))){end=z.getTick();break;}}}
    if(b<v.drop)end=Math.min(end,(long)v.drop*ppq);
    double g=(ch==2&&b>=v.solo&&b<v.retorno)?.88:gain(b,v);
    if(ch==9&&v.tipo>=2)g*=.42;
    msg(output,144,ch,p,(int)Math.min(120,Math.max(1,Math.round(m.getData2()*g))),e.getTick());msg(output,128,ch,p,0,end);
   }
   int ch=ti==1?9:ti==2?1:2;msg(output,176,ch,91,ch==2?48:ch==9?24:12,0);
   msg(output,176,ch,123,0,v.drop*ppq);
  }
  Track rhythm=dst.createTrack();meta(rhythm,3,"Groove del genero",0);
  for(int bar=0;bar<306;bar+=4){
   double[] kicks=v.tipo<2?new double[]{0,1.5,2.5}:v.tipo==2?new double[]{0,.75,2,3.5}:v.tipo==3?new double[]{0,1.5,2.75}:new double[]{0,2};
   double[] snares=v.tipo<2?new double[]{1,3}:v.tipo<4?new double[]{1,2.5,3.25}:new double[]{.75,1.5,2.75,3.5};
   for(double x:kicks)addRhythm(rhythm,36,bar+x,98,v,ppq);
   for(double x:snares)addRhythm(rhythm,v.tipo<2?37:38,bar+x,v.tipo<2?67:91,v,ppq);
   for(double x=0;x<4;x+=.5)addRhythm(rhythm,42,bar+x,x%1==0?42:54,v,ppq);
  }
  Track shaker=dst.createTrack();meta(shaker,3,"Shaker por tiempo - ambiente exterior",0);Random rng=new Random(v.seed);
  Set<Long> melody=new HashSet<>();Track piano=dst.getTracks()[3];for(int i=0;i<piano.size();i++){MidiEvent e=piano.get(i);if(e.getMessage() instanceof ShortMessage&&((ShortMessage)e.getMessage()).getCommand()==144)melody.add(Math.round(e.getTick()/(double)ppq));}
  for(int b=0;b<305;b++)if(active(b,v)){
   int accent=(b%4==1||b%4==3)?14:0;
   int vel=(int)((65+accent+(melody.contains((long)b)?9:0)+rng.nextInt(7))*gain(b,v));
   note(shaker,9,70,vel,b,.12,ppq);
   if((v.tipo==1||v.tipo==3)&&b%4==3&&active(b+.5,v))note(shaker,9,70,(int)(vel*.38),b+.5,.09,ppq);
  }
  meta(conductor,6,"Fin",306L*ppq);return dst;
 }
 static void addRhythm(Track t,int p,double b,int vel,Variante v,int ppq)throws Exception{if(b<305&&active(b,v))note(t,9,p,(int)(vel*gain(b,v)),b,.12,ppq);}
 static void render(Sequence s,Variante v)throws Exception{
  AudioSynthesizer synth=(AudioSynthesizer)MidiSystem.getSynthesizer();AudioFormat format=new AudioFormat(SR,16,2,true,false);
  Map<String,Object> props=new HashMap<>();props.put("reverb",true);props.put("chorus",false);props.put("interpolation","linear");props.put("load default soundbank",false);
  System.out.println("Renderizando "+v.nombre);System.out.flush();
  AudioInputStream stream=synth.openStream(format,props);System.out.println("Sintetizador abierto");System.out.flush();Soundbank bank=MidiSystem.getSoundbank(new File("C:/Windows/System32/drivers/gm.dls"));System.out.println("Banco leido");System.out.flush();if(!synth.loadAllInstruments(bank))throw new IOException("No se pudo cargar gm.dls");System.out.println("Instrumentos cargados");System.out.flush();
  Receiver receiver=synth.getReceiver();List<MidiEvent> events=new ArrayList<>();Track[] tracks=s.getTracks();
  for(int ti=0;ti<tracks.length-1;ti++)for(int j=0;j<tracks[ti].size();j++)events.add(tracks[ti].get(j));events.sort(Comparator.comparingLong(MidiEvent::getTick));
  for(MidiEvent e:events)if(e.getMessage() instanceof ShortMessage)receiver.send(e.getMessage(),Math.round(e.getTick()/(double)s.getResolution()*SEC*1e6));
  System.out.println("Eventos programados; sintetizando audio");System.out.flush();
  int frames=(int)((306*SEC+3.5)*SR);byte[] data=new byte[frames*4];int read=0,n;while(read<data.length&&(n=stream.read(data,read,Math.min(16384,data.length-read)))>0)read+=n;
  System.out.println("Audio sintetizado; procesando ambiente");System.out.flush();
  receiver.close();stream.close();synth.close();
  float[] sh=new float[frames];Random rng=new Random(v.seed);Track shaker=tracks[tracks.length-1];
  for(int j=0;j<shaker.size();j++){MidiEvent e=shaker.get(j);if(!(e.getMessage() instanceof ShortMessage))continue;ShortMessage m=(ShortMessage)e.getMessage();if(m.getCommand()!=144||m.getData2()==0)continue;int start=(int)(e.getTick()/(double)s.getResolution()*SEC*SR);double prev=0;
   for(int k=0;k<(int)(.13*SR)&&start+k<frames;k++){double noise=rng.nextDouble()*2-1;double high=noise-prev*.87;prev=noise;double env=Math.min(1,k/(.003*SR))*Math.exp(-k/(.028*SR));sh[start+k]+=(float)(high*env*m.getData2()/127.0*.17);}
  }
  // Reflexiones estereo difusas, con ecos al pulso de la melodia (124 BPM).
  double[] delays={.029,.043,.067,.089,SEC/2,SEC*.75,SEC,SEC*1.5,SEC*2};
  float[] mix=new float[frames*2];double peak=0,sum=0;
  for(int i=0;i<frames;i++)for(int ch=0;ch<2;ch++){
   int pos=i*4+ch*2;double a=(short)((data[pos]&255)|(data[pos+1]<<8))/32768.0;double spatial=sh[i]*.70;
   for(int d=0;d<delays.length;d++){int lag=(int)((delays[d]+(ch==0?0:.009+(d%3)*.004))*SR);int idx=i-lag;if(idx>2)spatial+=v.wet*Math.pow(.76,d)*.36*(sh[idx]+sh[idx-1]+sh[idx-2])/3;}
   // Dejar caer la cola al drop; el pasaje de piano queda solo.
   double beat=i/(double)SR/SEC;if(beat>=v.drop&&beat<v.solo)spatial*=Math.max(0,1-(beat-v.drop)/.65);
   if(beat>=v.solo&&beat<v.retorno)spatial=0;
   a+=spatial;mix[2*i+ch]=(float)a;peak=Math.max(peak,Math.abs(a));sum+=a*a;
  }
  double normalization=.89/Math.max(peak,.001);
  for(int i=0;i<mix.length;i++){int sample=(int)Math.round(mix[i]*normalization*32767);data[2*i]=(byte)sample;data[2*i+1]=(byte)(sample>>8);}
  AudioSystem.write(new AudioInputStream(new ByteArrayInputStream(data),format,frames),AudioFileFormat.Type.WAVE,OUT.resolve(v.nombre+".wav").toFile());
  System.out.printf(Locale.ROOT,"%s: %.2f s, peak %.3f, RMS %.4f, drop %.2f s, solo %.2f s, regreso %.2f s%n",v.nombre,frames/(double)SR,.89,Math.sqrt(sum/mix.length)*normalization,v.drop*SEC,v.solo*SEC,v.retorno*SEC);
 }
 public static void main(String[] args)throws Exception{System.setProperty("java.util.prefs.PreferencesFactory",MemoryFactory.class.getName());Files.createDirectories(OUT);for(Variante v:variantes){Sequence s=arrange(v);MidiSystem.write(s,1,OUT.resolve(v.nombre+".mid").toFile());render(s,v);}}
}
