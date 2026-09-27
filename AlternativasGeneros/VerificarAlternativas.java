import javax.sound.midi.*;
import javax.sound.sampled.*;
import java.io.*;
import java.nio.file.*;
import java.util.*;
public class VerificarAlternativas {
 public static void main(String[] args)throws Exception{
  int count=0;
  try(DirectoryStream<Path> paths=Files.newDirectoryStream(Paths.get("AlternativasGeneros"),"*.mid")){
   for(Path path:paths){if(path.getFileName().toString().endsWith("_Jython.mid"))continue;Sequence s=MidiSystem.getSequence(path.toFile());Map<String,Long> marks=new HashMap<>();int soloNotes=0,shakers=0,returns=0;
    for(Track t:s.getTracks())for(int i=0;i<t.size();i++){MidiEvent e=t.get(i);if(e.getMessage() instanceof MetaMessage){MetaMessage m=(MetaMessage)e.getMessage();if(m.getType()==6)marks.put(new String(m.getData(),"UTF-8"),e.getTick());}}
    long drop=marks.get("DROP: corte del conjunto"),solo=marks.get("Piano solo"),ret=marks.get("Regreso con toda la energia");
    for(Track t:s.getTracks())for(int i=0;i<t.size();i++){MidiEvent e=t.get(i);if(!(e.getMessage() instanceof ShortMessage))continue;ShortMessage m=(ShortMessage)e.getMessage();if(m.getCommand()!=144||m.getData2()==0)continue;long tick=e.getTick();
     if(tick>=drop&&tick<solo)throw new Exception("Ataque durante el drop: "+path);
     if(tick>=solo&&tick<ret){if(m.getChannel()!=2)throw new Exception("Otro instrumento durante el solo: "+path);soloNotes++;}
     if(tick>=ret&&tick<ret+8*s.getResolution())returns|=1<<m.getChannel();
     if(m.getChannel()==9&&m.getData1()==70)shakers++;
    }
    if(soloNotes==0||shakers<250||(returns&518)!=518)throw new Exception("Falta solo, shaker o conjunto: "+path);
    Path wav=path.resolveSibling(path.getFileName().toString().replace(".mid",".wav"));double peak=0;long samples=0;double energy=0;
    try(AudioInputStream in=AudioSystem.getAudioInputStream(wav.toFile())){byte[] bytes=new byte[16384];int n;while((n=in.read(bytes))!=-1)for(int i=0;i<n;i+=2){double a=(short)((bytes[i]&255)|(bytes[i+1]<<8))/32768.0;peak=Math.max(peak,Math.abs(a));energy+=a*a;samples++;}}
    if(peak>=.999||energy==0)throw new Exception("Audio saturado o vacio: "+wav);
    System.out.printf(Locale.ROOT,"OK %s: %d ataques de shaker, %d notas de piano solo, retorno completo, pico %.3f, RMS %.4f%n",path.getFileName(),shakers,soloNotes,peak,Math.sqrt(energy/samples));count++;
   }
  }
  if(count!=5)throw new Exception("Se esperaban cinco alternativas, hay "+count);
 }
}
